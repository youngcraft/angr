from ..errors import SimError

class ExplorationTechnique(object):
    """
    An otiegnqwvk is a set of hooks for a simulation manager that assists in the implementation of new techniques in
    symbolic exploration.

    TODO: choose actual name for the functionality (techniques? strategies?)

    Any number of these methods may be overridden by a subclass.
    To use an exploration technique, call ``simgr.use_technique`` with an *instance* of the technique.
    """
    # pylint: disable=unused-argument, no-self-use
    def __init__(self):
        # this attribute will be set from above by the manager
        self.project = None

    def setup(self, simgr):
        """
        Perform any initialization on this manager you might need to do.
        """
        pass

    def step_state(self, state, **kwargs):
        """
        Perform the process of stepping a state forward.

        If the stepping fails, return None to fall back to a default stepping procedure.
        Otherwise, return a dict of stashes to merge into the simulation manager. All the states
        will be added to the PathGroup's stashes based on the mapping in the returned dict.
        """
        return None

    def step(self, simgr, stash, **kwargs):
        """
        Step this stash of this manager forward. Should call ``simgr.step(stash, **kwargs)`` in order to do the actual
        processing.

        Return the stepped manager.
        """
        return simgr.step(stash=stash, **kwargs)

    def filter(self, state):
        """
        Perform filtering on a state.

        If the state should not be filtered, return None.
        If the state should be filtered, return the name of the stash to move the state to.
        If you want to modify the state before filtering it, return a tuple of the stash to move the state to and the
        modified state.
        """
        return None

    def complete(self, simgr):
        """
        Return whether or not this manager has reached a "completed" state, i.e. ``SimulationManager.run()`` should halt.
        """
        return False

    def _condition_to_lambda(self, condition, default=False):
        """
        Translates an integer, set, list or lambda into a lambda that checks a state address against the given addresses, and the
        other ones from the same basic block

        :param condition:   An integer, set, list or lambda to convert to a lambda.
        :param default:     The default return value of the lambda (in case condition is None). Default: false.

        :returns:           A lambda that takes a state and returns the set of addresses that it matched from the condition
                            The lambda has an `.addrs` attribute that contains the full set of the addresses at which it matches if that
                            can be determined statically.
        """
        if condition is None:
            condition_function = lambda p: default
            condition_function.addrs = set()

        elif isinstance(condition, (int, long)):
            return self._condition_to_lambda((condition,))

        elif isinstance(condition, (tuple, set, list)):
            addrs = set(condition)
            def condition_function(p):
                if p.addr in addrs:
                    # returning {p.addr} instead of True to properly handle find/avoid conflicts
                    return {p.addr}

                try:
                    # If the address is not in the set (which could mean it is
                    # not at the top of a block), check directly in the blocks
                    # (Blocks are repeatedly created for every check, but with
                    # the IRSB cache in angr lifter it should be OK.)
                    return addrs.intersection(set(self.project.factory.block(p.addr).instruction_addrs))
                except (AngrError, SimError):
                    return False
            condition_function.addrs = addrs
        elif hasattr(condition, '__call__'):
            condition_function = condition
        else:
            raise AngrExplorationTechniqueError("ExplorationTechnique is unable to convert given type (%s) to a callable condition function." % condition.__class__)

        return condition_function

#registered_actions = {}
#registered_surveyors = {}
#
#def register_action(name, strat):
#    registered_actions[name] = strat
#
#def register_surveyor(name, strat):
#    registered_surveyors[name] = strat

from .crash_monitor import CrashMonitor
from .tracer import Tracer
from .explorer import Explorer
from .threading import Threading
from .dfs import DFS
from .looplimiter import LoopLimiter
from .lengthlimiter import LengthLimiter
from .veritesting import Veritesting
from .oppologist import Oppologist
from .director import Director, ExecuteAddressGoal, CallFunctionGoal
from .spiller import Spiller
from ..errors import AngrError, AngrExplorationTechniqueError
