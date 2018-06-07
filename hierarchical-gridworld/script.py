from main import *
import worlds


def main():
    with Context() as context:
        world = worlds.default_world()
        init_message = messages.Message("[] is a grid",
                                        messages.WorldMessage(world))
        machine = RegisterMachine(context=context, use_cache=False) 
        machine = machine.add_register(init_message)
        return run_machine(machine)


if __name__ == "__main__":
    try:
        message, state, src = main()
        import IPython
        from worlds import display_history
        IPython.embed()
    except (KeyboardInterrupt, ChangedContinuationError):
        pass
