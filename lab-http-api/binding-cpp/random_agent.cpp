#include "include/lab/lab.h"

static
void run_single_environment(
	const boost::shared_ptr<Lab::Client>& client,
	const std::string& env_id,
	int episodes_to_run)
{
	boost::shared_ptr<Lab::Environment> env = client->make(env_id);
	boost::shared_ptr<Lab::Space> action_space = env->action_space();
	boost::shared_ptr<Lab::Space> observation_space = env->observation_space();

	for (int e=0; e<episodes_to_run; ++e) {
		printf("%s episode %i...\n", env_id.c_str(), e);
		Lab::State s;
		env->reset(&s);
		float total_reward = 0;
		int total_steps = 0;
		while (1) {
			std::vector<float> action = action_space->sample();
			env->step(action, true, &s);
			assert(s.observation.size()==observation_space->sample().size());
			total_reward += s.reward;
			total_steps += 1;
			if (s.done) break;
		}
		printf("%s episode %i finished in %i steps with reward %0.2f\n",
			env_id.c_str(), e, total_steps, total_reward);
	}
}

int main(int argc, char** argv)
{
	try {
		boost::shared_ptr<Lab::Client> client = Lab::client_create("127.0.0.1", 5000);
		run_single_environment(client, "Breakout-v0", 3);

	} catch (const std::exception& e) {
		fprintf(stderr, "ERROR: %s\n", e.what());
		return 1;
	}

	return 0;
}
