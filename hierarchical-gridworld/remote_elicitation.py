import datetime
import worlds
import main
import messages
import suggestions
import pytz
from collections import defaultdict
from human_feedback_api import Feedback


def now():
    return datetime.datetime.now(pytz.utc)


class ServerContext(object):

    supports_pre_suggestions = False

    def __init__(self, experiment_name="gridworld-test", is_sandbox=False):
        self.experiment_name = experiment_name
        self.queried = set()
        self.last_time = now()
        self.results = {}
        self.is_sandbox = is_sandbox
        fs = Feedback.objects.filter(responded_at__isnull=True,
                                     experiment_name=self.experiment_name)
        fs.update(canceled_at=now())

    def __enter__(self):
        self.suggesters = {
            "implement": suggestions.Suggester("implement",
                                               num_suggestions=15),
            "translate": suggestions.Suggester("translate",
                                               num_suggestions=15),
        }
        return self

    def __exit__(self, *args):
        for v in self.suggesters.values():
            v.close()

    def delete_cached_response(self, obs):
        if obs in self.results:
            print("deleting {}".format(obs))
            del self.results[obs]

    def sweep(self):
        new_results = set()
        for f in Feedback.objects.filter(responded_at__gt=self.last_time,
                                         experiment_name=self.experiment_name):
            self.last_time = max(self.last_time, f.responded_at)
            self.results[f.dialog_context] = (f.response, f.rater)
            new_results.add(f.dialog_context)
            #obs may not be in queried if it was pending when self was created
            if f.dialog_context in self.queried:
                self.queried.remove(f.dialog_context)
        return new_results

    def get_response(self, env, obs, suggestions=[], **kwargs):
        if obs in self.results:
            response, rater = self.results[obs]
            return response, "remote:{}".format(rater)
        if obs not in self.queried:
            print("querying server")
            print(obs)
            print("suggestions: {}".format(suggestions))
            f = Feedback(response_kind="free_response",
                         dialog_context=obs,
                         priority=0,
                         suggestions="\n".join(suggestions),
                         experiment_name=self.experiment_name)
            f.full_clean()
            f.save()
            self.queried.add(obs)
        raise WaitingOnServer(env, obs)


class WaitingOnServer(Exception):
    def __init__(self, env, obs):
        self.obs = obs
        self.env = env


def default_machine(context):
    world = worlds.default_world()
    Q = messages.Message(
        "move the agent to the goal in grid []", messages.WorldMessage(world))
    budget = 100000
    machine = main.RegisterMachine(context=context, nominal_budget=budget)
    return machine.add_register(machine.make_head(Q, budget))


def run_many_machines():
    with ServerContext() as context:
        waiting = defaultdict(list)
        results = []
        machines = []
        active_machines = 15
        try:
            while True:
                while (len(machines) + sum(len(v) for v in waiting.values()) <
                       active_machines):
                    machines.append(default_machine(context))
                if machines:
                    machine = machines.pop()
                    try:
                        results.append(main.run_machine(machine))
                    except WaitingOnServer as e:
                        waiting[e.obs].append(e.env)
                elif waiting:
                    for obs in context.sweep():
                        machines.extend(waiting[obs])
                        del waiting[obs]
                else:
                    return results
        except KeyboardInterrupt:
            import IPython
            IPython.embed()


if __name__ == '__main__':
    run_many_machines()
