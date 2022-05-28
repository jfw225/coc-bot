

from typing import Iterable


class SharedVariables:
    """ Used to share variables between states. """

    def __init__(self):
        pass


class State:
    class Exit:
        pass

    def __init__(self, shared: SharedVariables = SharedVariables()):
        # keep shared variable space
        self.SHARED = shared

    def __call__(self):
        return self.transition(self.SHARED)

    def transition(self, sh: SharedVariables):
        """ 
        Does an action and returns an output state type. This should be 
        overloaded. 
        """

        return State


class FiniteStateMachine:
    """ Finite State Machine. """

    def __init__(self,
                 shared: SharedVariables,
                 *states: Iterable["State"],
                 start_state: State = None):

        # maps class types to initialized objects
        self._state_map = {state: state(shared) for state in states}

        # set starting state
        self._start_state = start_state
        if start_state is None:
            self._start_state, *_ = self._state_map.values()

    def __getitem__(self, key: State):
        return self._state_map[key]

    def run(self):
        """ The main run loop. """

        state = self._start_state

        try:
            while True:
                state = self[state()]

                if state is State.Exit:
                    break
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    shared = SharedVariables()
    state = State()

    fsm = FiniteStateMachine(state)
    fsm.run()
