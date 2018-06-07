from remote_elicitation import ServerContext, WaitingOnServer
import messages
import worlds
import main
from collections import defaultdict

def default_machine(context):
    world = worlds.default_world()
    Q = messages.Message("[] is a grid", messages.WorldMessage(world))
    budget = 100000
    machine = main.RegisterMachine(context=context, nominal_budget=budget)
    return machine.add_register(Q)

#XXX this is very hacky
def run_sandboxes():
    active_machines = 10
    try:
        contexts = [ServerContext("sandbox-{}".format(i), is_sandbox=True) for i in range(active_machines)]
        for context in contexts:
            context.__enter__()
        machines = [default_machine(context) for context in contexts]
        waiting = defaultdict(list)
        results = []
        while True:
            if machines:
                machine = machines.pop()
                try:
                    results.append(main.run_machine(machine))
                    machine.context.results = {}
                    machines.append(default_machine(machine.context))
                except WaitingOnServer as e:
                    waiting[e.obs].append(e.env)
            elif waiting:
                for context in contexts:
                    for obs in context.sweep():
                        machines.extend(waiting[obs])
                        del waiting[obs]
            else:
                return results
    finally:
        for context in contexts: context.__exit__()

if __name__ == '__main__':
    run_sandboxes()
