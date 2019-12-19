import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
@SuppressWarnings({"NonAtomicOperationOnVolatileField", "FieldCanBeLocal", "InnerClassMayBeStatic", "DuplicatedCode", "MismatchedReadAndWriteOfArray", "unused", "SpellCheckingInspection"})
public class dve_exit_5 {
    // The objects in the model.
    private final SLCO_Class[] objects;

    // Upperbound for transition counter
    private static final long COUNTER_BOUND = 300000000L;

    // Lock class to handle locks of global variables
	private static class LockManager {
        // The locks
        private final ReentrantLock[] locks;

		// Constructor
		LockManager(int noVariables) {
			locks = new ReentrantLock[noVariables];
			Arrays.fill(locks, new ReentrantLock(true));
		}

		// Lock method
		void lock(int... lock_ids) {
		    Arrays.sort(lock_ids);
		    int last_lock_id = -1;
			for (int lock_id : lock_ids) {
			    if(lock_id != last_lock_id) {
                    locks[lock_id].lock();
			        last_lock_id = lock_id;
			    }
      		}
		}

		// Unlock method
		void unlock(int... lock_ids) {
		    Arrays.sort(lock_ids);
		    int last_lock_id = -1;
			for (int lock_id : lock_ids) {
			    if(lock_id != last_lock_id) {
                    locks[lock_id].unlock();
                }
      		}
		}
	}

    interface SLCO_Class {
        void startThreads();
        void joinThreads();
    }

    // representation of a class
    private static class GlobalClass implements SLCO_Class {
        // The threads
        private final TimerThread T_Timer;
        private final Person_0Thread T_Person_0;
        private final Person_1Thread T_Person_1;
        private final Person_2Thread T_Person_2;

        // Global variables
        private volatile byte time;
        private volatile byte[] done;
        private volatile byte atmodul;
        private volatile byte body;
        private volatile byte[] solved;

        interface GlobalClass_TimerThread_States {
            enum States {
                q
            }
        }

        class TimerThread extends Thread implements GlobalClass_TimerThread_States {
            // Current state
            private TimerThread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            TimerThread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = TimerThread.States.q;
            }

            private boolean exec_q() {
                lockManager.lock(3, 4, 5, 2); // Acquire [done[0], done[1], done[2], time]
                if (time < 6) { // from q to q {[time < 6; done[0] = 0; done[1] = 0; done[2] = 0; time = time + 1]} 
                    done[0] = (byte) (0);
                    done[1] = (byte) (0);
                    done[2] = (byte) (0);
                    time = (byte) (time + 1);
                    lockManager.unlock(3, 4, 5, 2); // Release [done[0], done[1], done[2], time]
                    currentState = TimerThread.States.q;
                    return true;
                }
                lockManager.unlock(3, 4, 5, 2); // Release [done[0], done[1], done[2], time]
                return false;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    switch(currentState) {
                        case q:
                            result = exec_q();
                            break;
                        default:
                            return;
                    }

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
            }

            // Run method
            public void run() {
                exec();
            }
        }

        interface GlobalClass_Person_0Thread_States {
            enum States {
                Studovna, Moravak, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Person_0Thread extends Thread implements GlobalClass_Person_0Thread_States {
            // Current state
            private Person_0Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            Person_0Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = Person_0Thread.States.Studovna;
            }

            private boolean exec_Studovna() {
                // from Studovna to Studovna {[done[0] = 0 and solved[9] = 0 and time >= 7 and time <= 6; done[0] = 1; solved[9] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[0] = 0 and solved[11] = 0 and time >= 7 and time <= 6; done[0] = 1; solved[11] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[0] = 0 and solved[12] = 0 and time >= 9 and time <= 6; done[0] = 1; solved[12] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[0] = 0 and solved[15] = 0 and time >= 11 and time <= 6; done[0] = 1; solved[15] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 3, 12, 2); // Acquire [body, done[0], solved[6], time]
                        if (done[0] == 0 && solved[6] == 0 && time >= 3 && time <= 6) { // from Studovna to Studovna {[done[0] = 0 and solved[6] = 0 and time >= 3 and time <= 6; done[0] = 1; solved[6] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 12, 2); // Release [body, done[0], solved[6], time]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 3, 12, 2); // Release [body, done[0], solved[6], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 3, 16, 2); // Acquire [body, done[0], solved[10], time]
                        if (done[0] == 0 && solved[10] == 0 && time >= 6 && time <= 6) { // from Studovna to Studovna {[done[0] = 0 and solved[10] = 0 and time >= 6 and time <= 6; done[0] = 1; solved[10] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 16, 2); // Release [body, done[0], solved[10], time]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 3, 16, 2); // Release [body, done[0], solved[10], time]
                        return false;
                    case 2:
                        lockManager.lock(1, 3, 9, 2); // Acquire [body, done[0], solved[3], time]
                        if (done[0] == 0 && solved[3] == 0 && time >= 2 && time <= 6) { // from Studovna to Studovna {[done[0] = 0 and solved[3] = 0 and time >= 2 and time <= 6; done[0] = 1; solved[3] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 9, 2); // Release [body, done[0], solved[3], time]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 3, 9, 2); // Release [body, done[0], solved[3], time]
                        return false;
                    case 3:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Studovna to Moravak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 4:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Studovna to Spilberk {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 5:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Studovna to Svobodak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Moravak() {
                switch(random.nextInt(7)) {
                    case 0:
                        lockManager.lock(1, 3, 13, 2); // Acquire [body, done[0], solved[7], time]
                        if (done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Moravak to Moravak {[done[0] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[0] = 1; solved[7] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 13, 2); // Release [body, done[0], solved[7], time]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(1, 3, 13, 2); // Release [body, done[0], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Moravak to Jaroska {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 2:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Moravak to Studovna {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 3:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Moravak to Svobodak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 4:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Moravak to Tyrs {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 5:
                        lockManager.lock(3, 22, 24); // Acquire [done[0], solved[16], solved[18]]
                        if (solved[16] == 1 && done[0] == 0) { // from Moravak to Moravak {[solved[16] = 1 and done[0] = 0; done[0] = 1; solved[18] = 1]} 
                            done[0] = (byte) (1);
                            solved[18] = (byte) (1);
                            lockManager.unlock(3, 22, 24); // Release [done[0], solved[16], solved[18]]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(3, 22, 24); // Release [done[0], solved[16], solved[18]]
                        return false;
                    case 6:
                        lockManager.lock(3, 23, 25); // Acquire [done[0], solved[17], solved[19]]
                        if (done[0] == 0 && solved[19] == 1 && solved[17] == 1) { // from Moravak to Burian {[done[0] = 0 and solved[19] = 1 and solved[17] = 1; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3, 23, 25); // Release [done[0], solved[17], solved[19]]
                            currentState = Person_0Thread.States.Burian;
                            return true;
                        }
                        lockManager.unlock(3, 23, 25); // Release [done[0], solved[17], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Ceska() {
                // There are no transitions to be made.
                return false;
            }

            private boolean exec_Svobodak() {
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 3, 11, 13, 2); // Acquire [body, done[0], solved[5], solved[7], time]
                        if (done[0] == 0 && solved[5] == 0 && time >= 5 && time <= 5) { // from Svobodak to Svobodak {[done[0] = 0 and solved[5] = 0 and time >= 5 and time <= 5; done[0] = 1; solved[5] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 11, 13, 2); // Release [body, done[0], solved[5], solved[7], time]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        } else if(done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Svobodak to Svobodak {[done[0] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[0] = 1; solved[7] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 11, 13, 2); // Release [body, done[0], solved[5], solved[7], time]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 3, 11, 13, 2); // Release [body, done[0], solved[5], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 3, 23); // Acquire [body, done[0], solved[17]]
                        if (body >= 10 && done[0] == 0) { // from Svobodak to Svobodak {[body >= 10 and done[0] = 0; done[0] = 1; solved[17] = 1]} 
                            done[0] = (byte) (1);
                            solved[17] = (byte) (1);
                            lockManager.unlock(1, 3, 23); // Release [body, done[0], solved[17]]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 3, 23); // Release [body, done[0], solved[17]]
                        return false;
                    case 2:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Svobodak to Malinak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 3:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Svobodak to Moravak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 4:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Svobodak to Petrov {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 5:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Svobodak to Studovna {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Petrov() {
                switch(random.nextInt(4)) {
                    case 0:
                        lockManager.lock(1, 3, 22); // Acquire [body, done[0], solved[16]]
                        if (body >= 10 && done[0] == 0) { // from Petrov to Petrov {[body >= 10 and done[0] = 0; done[0] = 1; solved[16] = 1]} 
                            done[0] = (byte) (1);
                            solved[16] = (byte) (1);
                            lockManager.unlock(1, 3, 22); // Release [body, done[0], solved[16]]
                            currentState = Person_0Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 3, 22); // Release [body, done[0], solved[16]]
                        return false;
                    case 1:
                        lockManager.lock(1, 3, 6, 10, 2); // Acquire [body, done[0], solved[0], solved[4], time]
                        if (done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Petrov to Petrov {[done[0] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[0] = 1; solved[0] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 6, 10, 2); // Release [body, done[0], solved[0], solved[4], time]
                            currentState = Person_0Thread.States.Petrov;
                            return true;
                        } else if(done[0] == 0 && solved[4] == 0 && time >= 5 && time <= 5) { // from Petrov to Petrov {[done[0] = 0 and solved[4] = 0 and time >= 5 and time <= 5; done[0] = 1; solved[4] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 6, 10, 2); // Release [body, done[0], solved[0], solved[4], time]
                            currentState = Person_0Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 3, 6, 10, 2); // Release [body, done[0], solved[0], solved[4], time]
                        return false;
                    case 2:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Petrov to Spilberk {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 3:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Petrov to Svobodak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Spilberk() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 3, 7, 14, 2); // Acquire [body, done[0], solved[1], solved[8], time]
                        if (done[0] == 0 && solved[1] == 0 && time >= 0 && time <= 4) { // from Spilberk to Spilberk {[done[0] = 0 and solved[1] = 0 and time >= 0 and time <= 4; done[0] = 1; solved[1] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 7, 14, 2); // Release [body, done[0], solved[1], solved[8], time]
                            currentState = Person_0Thread.States.Spilberk;
                            return true;
                        } else if(done[0] == 0 && solved[8] == 0 && time >= 8 && time <= 9) { // from Spilberk to Spilberk {[done[0] = 0 and solved[8] = 0 and time >= 8 and time <= 9; done[0] = 1; solved[8] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 7, 14, 2); // Release [body, done[0], solved[1], solved[8], time]
                            currentState = Person_0Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(1, 3, 7, 14, 2); // Release [body, done[0], solved[1], solved[8], time]
                        return false;
                    case 1:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Spilberk to Petrov {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 2:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Spilberk to Studovna {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Malinak() {
                // from Malinak to Malinak {[done[0] = 0 and solved[13] = 0 and time >= 12 and time <= 6; done[0] = 1; solved[13] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 3, 13, 2); // Acquire [body, done[0], solved[7], time]
                        if (done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Malinak to Malinak {[done[0] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[0] = 1; solved[7] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 13, 2); // Release [body, done[0], solved[7], time]
                            currentState = Person_0Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(1, 3, 13, 2); // Release [body, done[0], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Malinak to Svobodak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Jaroska() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 3, 6, 2); // Acquire [body, done[0], solved[0], time]
                        if (done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Jaroska to Jaroska {[done[0] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[0] = 1; solved[0] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 6, 2); // Release [body, done[0], solved[0], time]
                            currentState = Person_0Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(1, 3, 6, 2); // Release [body, done[0], solved[0], time]
                        return false;
                    case 1:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Jaroska to Moravak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    case 2:
                        lockManager.lock(3, 24, 25); // Acquire [done[0], solved[18], solved[19]]
                        if (solved[18] == 1 && done[0] == 0) { // from Jaroska to Jaroska {[solved[18] = 1 and done[0] = 0; done[0] = 1; solved[19] = 1]} 
                            done[0] = (byte) (1);
                            solved[19] = (byte) (1);
                            lockManager.unlock(3, 24, 25); // Release [done[0], solved[18], solved[19]]
                            currentState = Person_0Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(3, 24, 25); // Release [done[0], solved[18], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Tyrs() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 3, 20, 8, 2); // Acquire [body, done[0], solved[14], solved[2], time]
                        if (done[0] == 0 && solved[14] == 0 && time >= 9 && time <= 13) { // from Tyrs to Tyrs {[done[0] = 0 and solved[14] = 0 and time >= 9 and time <= 13; done[0] = 1; solved[14] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 20, 8, 2); // Release [body, done[0], solved[14], solved[2], time]
                            currentState = Person_0Thread.States.Tyrs;
                            return true;
                        } else if(done[0] == 0 && solved[2] == 0 && time >= 1 && time <= 4) { // from Tyrs to Tyrs {[done[0] = 0 and solved[2] = 0 and time >= 1 and time <= 4; done[0] = 1; solved[2] = 1; body = body + 1]} 
                            done[0] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 3, 20, 8, 2); // Release [body, done[0], solved[14], solved[2], time]
                            currentState = Person_0Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(1, 3, 20, 8, 2); // Release [body, done[0], solved[14], solved[2], time]
                        return false;
                    case 1:
                        lockManager.lock(3); // Acquire [done[0]]
                        if (done[0] == 0) { // from Tyrs to Moravak {[done[0] = 0; done[0] = 1]} 
                            done[0] = (byte) (1);
                            lockManager.unlock(3); // Release [done[0]]
                            currentState = Person_0Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(3); // Release [done[0]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Burian() {
                lockManager.lock(3); // Acquire [done[0]]
                if (done[0] == 0) { // from Burian to Wilson {[done[0] = 0; done[0] = 1]} 
                    done[0] = (byte) (1);
                    lockManager.unlock(3); // Release [done[0]]
                    currentState = Person_0Thread.States.Wilson;
                    return true;
                }
                lockManager.unlock(3); // Release [done[0]]
                return false;
            }

            private boolean exec_Wilson() {
                lockManager.lock(0, 3); // Acquire [atmodul, done[0]]
                if (done[0] == 0) { // from Wilson to Modul {[done[0] = 0; atmodul = atmodul + 1; done[0] = 1]} 
                    atmodul = (byte) (atmodul + 1);
                    done[0] = (byte) (1);
                    lockManager.unlock(0, 3); // Release [atmodul, done[0]]
                    currentState = Person_0Thread.States.Modul;
                    return true;
                }
                lockManager.unlock(0, 3); // Release [atmodul, done[0]]
                return false;
            }

            private boolean exec_Modul() {
                // There are no transitions to be made.
                return false;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    switch(currentState) {
                        case Studovna:
                            result = exec_Studovna();
                            break;
                        case Moravak:
                            result = exec_Moravak();
                            break;
                        case Ceska:
                            result = exec_Ceska();
                            break;
                        case Svobodak:
                            result = exec_Svobodak();
                            break;
                        case Petrov:
                            result = exec_Petrov();
                            break;
                        case Spilberk:
                            result = exec_Spilberk();
                            break;
                        case Malinak:
                            result = exec_Malinak();
                            break;
                        case Jaroska:
                            result = exec_Jaroska();
                            break;
                        case Tyrs:
                            result = exec_Tyrs();
                            break;
                        case Burian:
                            result = exec_Burian();
                            break;
                        case Wilson:
                            result = exec_Wilson();
                            break;
                        case Modul:
                            result = exec_Modul();
                            break;
                        default:
                            return;
                    }

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
            }

            // Run method
            public void run() {
                exec();
            }
        }

        interface GlobalClass_Person_1Thread_States {
            enum States {
                Moravak, Studovna, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Person_1Thread extends Thread implements GlobalClass_Person_1Thread_States {
            // Current state
            private Person_1Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            Person_1Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = Person_1Thread.States.Moravak;
            }

            private boolean exec_Moravak() {
                switch(random.nextInt(7)) {
                    case 0:
                        lockManager.lock(1, 4, 13, 2); // Acquire [body, done[1], solved[7], time]
                        if (done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Moravak to Moravak {[done[1] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[1] = 1; solved[7] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 13, 2); // Release [body, done[1], solved[7], time]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(1, 4, 13, 2); // Release [body, done[1], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Moravak to Jaroska {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 2:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Moravak to Studovna {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 3:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Moravak to Svobodak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 4:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Moravak to Tyrs {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 5:
                        lockManager.lock(4, 22, 24); // Acquire [done[1], solved[16], solved[18]]
                        if (solved[16] == 1 && done[1] == 0) { // from Moravak to Moravak {[solved[16] = 1 and done[1] = 0; done[1] = 1; solved[18] = 1]} 
                            done[1] = (byte) (1);
                            solved[18] = (byte) (1);
                            lockManager.unlock(4, 22, 24); // Release [done[1], solved[16], solved[18]]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(4, 22, 24); // Release [done[1], solved[16], solved[18]]
                        return false;
                    case 6:
                        lockManager.lock(4, 23, 25); // Acquire [done[1], solved[17], solved[19]]
                        if (done[1] == 0 && solved[19] == 1 && solved[17] == 1) { // from Moravak to Burian {[done[1] = 0 and solved[19] = 1 and solved[17] = 1; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4, 23, 25); // Release [done[1], solved[17], solved[19]]
                            currentState = Person_1Thread.States.Burian;
                            return true;
                        }
                        lockManager.unlock(4, 23, 25); // Release [done[1], solved[17], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Studovna() {
                // from Studovna to Studovna {[done[1] = 0 and solved[9] = 0 and time >= 7 and time <= 6; done[1] = 1; solved[9] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[1] = 0 and solved[11] = 0 and time >= 7 and time <= 6; done[1] = 1; solved[11] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[1] = 0 and solved[12] = 0 and time >= 9 and time <= 6; done[1] = 1; solved[12] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[1] = 0 and solved[15] = 0 and time >= 11 and time <= 6; done[1] = 1; solved[15] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 4, 12, 2); // Acquire [body, done[1], solved[6], time]
                        if (done[1] == 0 && solved[6] == 0 && time >= 3 && time <= 6) { // from Studovna to Studovna {[done[1] = 0 and solved[6] = 0 and time >= 3 and time <= 6; done[1] = 1; solved[6] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 12, 2); // Release [body, done[1], solved[6], time]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 4, 12, 2); // Release [body, done[1], solved[6], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 4, 16, 2); // Acquire [body, done[1], solved[10], time]
                        if (done[1] == 0 && solved[10] == 0 && time >= 6 && time <= 6) { // from Studovna to Studovna {[done[1] = 0 and solved[10] = 0 and time >= 6 and time <= 6; done[1] = 1; solved[10] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 16, 2); // Release [body, done[1], solved[10], time]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 4, 16, 2); // Release [body, done[1], solved[10], time]
                        return false;
                    case 2:
                        lockManager.lock(1, 4, 9, 2); // Acquire [body, done[1], solved[3], time]
                        if (done[1] == 0 && solved[3] == 0 && time >= 2 && time <= 6) { // from Studovna to Studovna {[done[1] = 0 and solved[3] = 0 and time >= 2 and time <= 6; done[1] = 1; solved[3] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 9, 2); // Release [body, done[1], solved[3], time]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 4, 9, 2); // Release [body, done[1], solved[3], time]
                        return false;
                    case 3:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Studovna to Moravak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 4:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Studovna to Spilberk {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 5:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Studovna to Svobodak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Ceska() {
                // There are no transitions to be made.
                return false;
            }

            private boolean exec_Svobodak() {
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 4, 11, 13, 2); // Acquire [body, done[1], solved[5], solved[7], time]
                        if (done[1] == 0 && solved[5] == 0 && time >= 5 && time <= 5) { // from Svobodak to Svobodak {[done[1] = 0 and solved[5] = 0 and time >= 5 and time <= 5; done[1] = 1; solved[5] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 11, 13, 2); // Release [body, done[1], solved[5], solved[7], time]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        } else if(done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Svobodak to Svobodak {[done[1] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[1] = 1; solved[7] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 11, 13, 2); // Release [body, done[1], solved[5], solved[7], time]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 4, 11, 13, 2); // Release [body, done[1], solved[5], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 4, 23); // Acquire [body, done[1], solved[17]]
                        if (body >= 10 && done[1] == 0) { // from Svobodak to Svobodak {[body >= 10 and done[1] = 0; done[1] = 1; solved[17] = 1]} 
                            done[1] = (byte) (1);
                            solved[17] = (byte) (1);
                            lockManager.unlock(1, 4, 23); // Release [body, done[1], solved[17]]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 4, 23); // Release [body, done[1], solved[17]]
                        return false;
                    case 2:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Svobodak to Malinak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 3:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Svobodak to Moravak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 4:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Svobodak to Petrov {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 5:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Svobodak to Studovna {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Petrov() {
                switch(random.nextInt(4)) {
                    case 0:
                        lockManager.lock(1, 4, 22); // Acquire [body, done[1], solved[16]]
                        if (body >= 10 && done[1] == 0) { // from Petrov to Petrov {[body >= 10 and done[1] = 0; done[1] = 1; solved[16] = 1]} 
                            done[1] = (byte) (1);
                            solved[16] = (byte) (1);
                            lockManager.unlock(1, 4, 22); // Release [body, done[1], solved[16]]
                            currentState = Person_1Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 4, 22); // Release [body, done[1], solved[16]]
                        return false;
                    case 1:
                        lockManager.lock(1, 4, 6, 10, 2); // Acquire [body, done[1], solved[0], solved[4], time]
                        if (done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Petrov to Petrov {[done[1] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[1] = 1; solved[0] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 6, 10, 2); // Release [body, done[1], solved[0], solved[4], time]
                            currentState = Person_1Thread.States.Petrov;
                            return true;
                        } else if(done[1] == 0 && solved[4] == 0 && time >= 5 && time <= 5) { // from Petrov to Petrov {[done[1] = 0 and solved[4] = 0 and time >= 5 and time <= 5; done[1] = 1; solved[4] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 6, 10, 2); // Release [body, done[1], solved[0], solved[4], time]
                            currentState = Person_1Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 4, 6, 10, 2); // Release [body, done[1], solved[0], solved[4], time]
                        return false;
                    case 2:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Petrov to Spilberk {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 3:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Petrov to Svobodak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Spilberk() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 4, 7, 14, 2); // Acquire [body, done[1], solved[1], solved[8], time]
                        if (done[1] == 0 && solved[1] == 0 && time >= 0 && time <= 4) { // from Spilberk to Spilberk {[done[1] = 0 and solved[1] = 0 and time >= 0 and time <= 4; done[1] = 1; solved[1] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 7, 14, 2); // Release [body, done[1], solved[1], solved[8], time]
                            currentState = Person_1Thread.States.Spilberk;
                            return true;
                        } else if(done[1] == 0 && solved[8] == 0 && time >= 8 && time <= 9) { // from Spilberk to Spilberk {[done[1] = 0 and solved[8] = 0 and time >= 8 and time <= 9; done[1] = 1; solved[8] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 7, 14, 2); // Release [body, done[1], solved[1], solved[8], time]
                            currentState = Person_1Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(1, 4, 7, 14, 2); // Release [body, done[1], solved[1], solved[8], time]
                        return false;
                    case 1:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Spilberk to Petrov {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 2:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Spilberk to Studovna {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Malinak() {
                // from Malinak to Malinak {[done[1] = 0 and solved[13] = 0 and time >= 12 and time <= 6; done[1] = 1; solved[13] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 4, 13, 2); // Acquire [body, done[1], solved[7], time]
                        if (done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Malinak to Malinak {[done[1] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[1] = 1; solved[7] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 13, 2); // Release [body, done[1], solved[7], time]
                            currentState = Person_1Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(1, 4, 13, 2); // Release [body, done[1], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Malinak to Svobodak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Jaroska() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 4, 6, 2); // Acquire [body, done[1], solved[0], time]
                        if (done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Jaroska to Jaroska {[done[1] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[1] = 1; solved[0] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 6, 2); // Release [body, done[1], solved[0], time]
                            currentState = Person_1Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(1, 4, 6, 2); // Release [body, done[1], solved[0], time]
                        return false;
                    case 1:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Jaroska to Moravak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    case 2:
                        lockManager.lock(4, 24, 25); // Acquire [done[1], solved[18], solved[19]]
                        if (solved[18] == 1 && done[1] == 0) { // from Jaroska to Jaroska {[solved[18] = 1 and done[1] = 0; done[1] = 1; solved[19] = 1]} 
                            done[1] = (byte) (1);
                            solved[19] = (byte) (1);
                            lockManager.unlock(4, 24, 25); // Release [done[1], solved[18], solved[19]]
                            currentState = Person_1Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(4, 24, 25); // Release [done[1], solved[18], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Tyrs() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 4, 20, 8, 2); // Acquire [body, done[1], solved[14], solved[2], time]
                        if (done[1] == 0 && solved[14] == 0 && time >= 9 && time <= 13) { // from Tyrs to Tyrs {[done[1] = 0 and solved[14] = 0 and time >= 9 and time <= 13; done[1] = 1; solved[14] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 20, 8, 2); // Release [body, done[1], solved[14], solved[2], time]
                            currentState = Person_1Thread.States.Tyrs;
                            return true;
                        } else if(done[1] == 0 && solved[2] == 0 && time >= 1 && time <= 4) { // from Tyrs to Tyrs {[done[1] = 0 and solved[2] = 0 and time >= 1 and time <= 4; done[1] = 1; solved[2] = 1; body = body + 1]} 
                            done[1] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 4, 20, 8, 2); // Release [body, done[1], solved[14], solved[2], time]
                            currentState = Person_1Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(1, 4, 20, 8, 2); // Release [body, done[1], solved[14], solved[2], time]
                        return false;
                    case 1:
                        lockManager.lock(4); // Acquire [done[1]]
                        if (done[1] == 0) { // from Tyrs to Moravak {[done[1] = 0; done[1] = 1]} 
                            done[1] = (byte) (1);
                            lockManager.unlock(4); // Release [done[1]]
                            currentState = Person_1Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(4); // Release [done[1]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Burian() {
                lockManager.lock(4); // Acquire [done[1]]
                if (done[1] == 0) { // from Burian to Wilson {[done[1] = 0; done[1] = 1]} 
                    done[1] = (byte) (1);
                    lockManager.unlock(4); // Release [done[1]]
                    currentState = Person_1Thread.States.Wilson;
                    return true;
                }
                lockManager.unlock(4); // Release [done[1]]
                return false;
            }

            private boolean exec_Wilson() {
                lockManager.lock(0, 4); // Acquire [atmodul, done[1]]
                if (done[1] == 0) { // from Wilson to Modul {[done[1] = 0; atmodul = atmodul + 1; done[1] = 1]} 
                    atmodul = (byte) (atmodul + 1);
                    done[1] = (byte) (1);
                    lockManager.unlock(0, 4); // Release [atmodul, done[1]]
                    currentState = Person_1Thread.States.Modul;
                    return true;
                }
                lockManager.unlock(0, 4); // Release [atmodul, done[1]]
                return false;
            }

            private boolean exec_Modul() {
                // There are no transitions to be made.
                return false;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    switch(currentState) {
                        case Moravak:
                            result = exec_Moravak();
                            break;
                        case Studovna:
                            result = exec_Studovna();
                            break;
                        case Ceska:
                            result = exec_Ceska();
                            break;
                        case Svobodak:
                            result = exec_Svobodak();
                            break;
                        case Petrov:
                            result = exec_Petrov();
                            break;
                        case Spilberk:
                            result = exec_Spilberk();
                            break;
                        case Malinak:
                            result = exec_Malinak();
                            break;
                        case Jaroska:
                            result = exec_Jaroska();
                            break;
                        case Tyrs:
                            result = exec_Tyrs();
                            break;
                        case Burian:
                            result = exec_Burian();
                            break;
                        case Wilson:
                            result = exec_Wilson();
                            break;
                        case Modul:
                            result = exec_Modul();
                            break;
                        default:
                            return;
                    }

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
            }

            // Run method
            public void run() {
                exec();
            }
        }

        interface GlobalClass_Person_2Thread_States {
            enum States {
                Moravak, Studovna, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Person_2Thread extends Thread implements GlobalClass_Person_2Thread_States {
            // Current state
            private Person_2Thread.States currentState;

            // Random number generator to handle non-determinism
            private final Random random;

            // Counter of main while-loop iterations
            long transition_counter;

            // Counter for successful iterations
            long successful_transition_counter;

            // The lock manager.
            private final LockManager lockManager;

            // Constructor
            Person_2Thread (LockManager lockManager) {
                random = new Random();
                this.lockManager = lockManager;
                transition_counter = 0;
                currentState = Person_2Thread.States.Moravak;
            }

            private boolean exec_Moravak() {
                switch(random.nextInt(7)) {
                    case 0:
                        lockManager.lock(1, 5, 13, 2); // Acquire [body, done[2], solved[7], time]
                        if (done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Moravak to Moravak {[done[2] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[2] = 1; solved[7] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 13, 2); // Release [body, done[2], solved[7], time]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(1, 5, 13, 2); // Release [body, done[2], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Moravak to Jaroska {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 2:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Moravak to Studovna {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 3:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Moravak to Svobodak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 4:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Moravak to Tyrs {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 5:
                        lockManager.lock(5, 22, 24); // Acquire [done[2], solved[16], solved[18]]
                        if (solved[16] == 1 && done[2] == 0) { // from Moravak to Moravak {[solved[16] = 1 and done[2] = 0; done[2] = 1; solved[18] = 1]} 
                            done[2] = (byte) (1);
                            solved[18] = (byte) (1);
                            lockManager.unlock(5, 22, 24); // Release [done[2], solved[16], solved[18]]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(5, 22, 24); // Release [done[2], solved[16], solved[18]]
                        return false;
                    case 6:
                        lockManager.lock(5, 23, 25); // Acquire [done[2], solved[17], solved[19]]
                        if (done[2] == 0 && solved[19] == 1 && solved[17] == 1) { // from Moravak to Burian {[done[2] = 0 and solved[19] = 1 and solved[17] = 1; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5, 23, 25); // Release [done[2], solved[17], solved[19]]
                            currentState = Person_2Thread.States.Burian;
                            return true;
                        }
                        lockManager.unlock(5, 23, 25); // Release [done[2], solved[17], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Studovna() {
                // from Studovna to Studovna {[done[2] = 0 and solved[9] = 0 and time >= 7 and time <= 6; done[2] = 1; solved[9] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[2] = 0 and solved[11] = 0 and time >= 7 and time <= 6; done[2] = 1; solved[11] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[2] = 0 and solved[12] = 0 and time >= 9 and time <= 6; done[2] = 1; solved[12] = 1; body = body + 1]} (trivially unsatisfiable)
                // from Studovna to Studovna {[done[2] = 0 and solved[15] = 0 and time >= 11 and time <= 6; done[2] = 1; solved[15] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 5, 12, 2); // Acquire [body, done[2], solved[6], time]
                        if (done[2] == 0 && solved[6] == 0 && time >= 3 && time <= 6) { // from Studovna to Studovna {[done[2] = 0 and solved[6] = 0 and time >= 3 and time <= 6; done[2] = 1; solved[6] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 12, 2); // Release [body, done[2], solved[6], time]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 5, 12, 2); // Release [body, done[2], solved[6], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 5, 16, 2); // Acquire [body, done[2], solved[10], time]
                        if (done[2] == 0 && solved[10] == 0 && time >= 6 && time <= 6) { // from Studovna to Studovna {[done[2] = 0 and solved[10] = 0 and time >= 6 and time <= 6; done[2] = 1; solved[10] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 16, 2); // Release [body, done[2], solved[10], time]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 5, 16, 2); // Release [body, done[2], solved[10], time]
                        return false;
                    case 2:
                        lockManager.lock(1, 5, 9, 2); // Acquire [body, done[2], solved[3], time]
                        if (done[2] == 0 && solved[3] == 0 && time >= 2 && time <= 6) { // from Studovna to Studovna {[done[2] = 0 and solved[3] = 0 and time >= 2 and time <= 6; done[2] = 1; solved[3] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 9, 2); // Release [body, done[2], solved[3], time]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(1, 5, 9, 2); // Release [body, done[2], solved[3], time]
                        return false;
                    case 3:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Studovna to Moravak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 4:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Studovna to Spilberk {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 5:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Studovna to Svobodak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Ceska() {
                // There are no transitions to be made.
                return false;
            }

            private boolean exec_Svobodak() {
                switch(random.nextInt(6)) {
                    case 0:
                        lockManager.lock(1, 5, 11, 13, 2); // Acquire [body, done[2], solved[5], solved[7], time]
                        if (done[2] == 0 && solved[5] == 0 && time >= 5 && time <= 5) { // from Svobodak to Svobodak {[done[2] = 0 and solved[5] = 0 and time >= 5 and time <= 5; done[2] = 1; solved[5] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 11, 13, 2); // Release [body, done[2], solved[5], solved[7], time]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        } else if(done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Svobodak to Svobodak {[done[2] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[2] = 1; solved[7] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 11, 13, 2); // Release [body, done[2], solved[5], solved[7], time]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 5, 11, 13, 2); // Release [body, done[2], solved[5], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(1, 5, 23); // Acquire [body, done[2], solved[17]]
                        if (body >= 10 && done[2] == 0) { // from Svobodak to Svobodak {[body >= 10 and done[2] = 0; done[2] = 1; solved[17] = 1]} 
                            done[2] = (byte) (1);
                            solved[17] = (byte) (1);
                            lockManager.unlock(1, 5, 23); // Release [body, done[2], solved[17]]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(1, 5, 23); // Release [body, done[2], solved[17]]
                        return false;
                    case 2:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Svobodak to Malinak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 3:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Svobodak to Moravak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 4:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Svobodak to Petrov {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 5:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Svobodak to Studovna {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Petrov() {
                switch(random.nextInt(4)) {
                    case 0:
                        lockManager.lock(1, 5, 22); // Acquire [body, done[2], solved[16]]
                        if (body >= 10 && done[2] == 0) { // from Petrov to Petrov {[body >= 10 and done[2] = 0; done[2] = 1; solved[16] = 1]} 
                            done[2] = (byte) (1);
                            solved[16] = (byte) (1);
                            lockManager.unlock(1, 5, 22); // Release [body, done[2], solved[16]]
                            currentState = Person_2Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 5, 22); // Release [body, done[2], solved[16]]
                        return false;
                    case 1:
                        lockManager.lock(1, 5, 6, 10, 2); // Acquire [body, done[2], solved[0], solved[4], time]
                        if (done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Petrov to Petrov {[done[2] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[2] = 1; solved[0] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 6, 10, 2); // Release [body, done[2], solved[0], solved[4], time]
                            currentState = Person_2Thread.States.Petrov;
                            return true;
                        } else if(done[2] == 0 && solved[4] == 0 && time >= 5 && time <= 5) { // from Petrov to Petrov {[done[2] = 0 and solved[4] = 0 and time >= 5 and time <= 5; done[2] = 1; solved[4] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 6, 10, 2); // Release [body, done[2], solved[0], solved[4], time]
                            currentState = Person_2Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(1, 5, 6, 10, 2); // Release [body, done[2], solved[0], solved[4], time]
                        return false;
                    case 2:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Petrov to Spilberk {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 3:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Petrov to Svobodak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Spilberk() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 5, 7, 14, 2); // Acquire [body, done[2], solved[1], solved[8], time]
                        if (done[2] == 0 && solved[1] == 0 && time >= 0 && time <= 4) { // from Spilberk to Spilberk {[done[2] = 0 and solved[1] = 0 and time >= 0 and time <= 4; done[2] = 1; solved[1] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 7, 14, 2); // Release [body, done[2], solved[1], solved[8], time]
                            currentState = Person_2Thread.States.Spilberk;
                            return true;
                        } else if(done[2] == 0 && solved[8] == 0 && time >= 8 && time <= 9) { // from Spilberk to Spilberk {[done[2] = 0 and solved[8] = 0 and time >= 8 and time <= 9; done[2] = 1; solved[8] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 7, 14, 2); // Release [body, done[2], solved[1], solved[8], time]
                            currentState = Person_2Thread.States.Spilberk;
                            return true;
                        }
                        lockManager.unlock(1, 5, 7, 14, 2); // Release [body, done[2], solved[1], solved[8], time]
                        return false;
                    case 1:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Spilberk to Petrov {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Petrov;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 2:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Spilberk to Studovna {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Studovna;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Malinak() {
                // from Malinak to Malinak {[done[2] = 0 and solved[13] = 0 and time >= 12 and time <= 6; done[2] = 1; solved[13] = 1; body = body + 1]} (trivially unsatisfiable)
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 5, 13, 2); // Acquire [body, done[2], solved[7], time]
                        if (done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) { // from Malinak to Malinak {[done[2] = 0 and solved[7] = 0 and time >= 6 and time <= 6; done[2] = 1; solved[7] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 13, 2); // Release [body, done[2], solved[7], time]
                            currentState = Person_2Thread.States.Malinak;
                            return true;
                        }
                        lockManager.unlock(1, 5, 13, 2); // Release [body, done[2], solved[7], time]
                        return false;
                    case 1:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Malinak to Svobodak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Svobodak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Jaroska() {
                switch(random.nextInt(3)) {
                    case 0:
                        lockManager.lock(1, 5, 6, 2); // Acquire [body, done[2], solved[0], time]
                        if (done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2) { // from Jaroska to Jaroska {[done[2] = 0 and solved[0] = 0 and time >= 0 and time <= 2; done[2] = 1; solved[0] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 6, 2); // Release [body, done[2], solved[0], time]
                            currentState = Person_2Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(1, 5, 6, 2); // Release [body, done[2], solved[0], time]
                        return false;
                    case 1:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Jaroska to Moravak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    case 2:
                        lockManager.lock(5, 24, 25); // Acquire [done[2], solved[18], solved[19]]
                        if (solved[18] == 1 && done[2] == 0) { // from Jaroska to Jaroska {[solved[18] = 1 and done[2] = 0; done[2] = 1; solved[19] = 1]} 
                            done[2] = (byte) (1);
                            solved[19] = (byte) (1);
                            lockManager.unlock(5, 24, 25); // Release [done[2], solved[18], solved[19]]
                            currentState = Person_2Thread.States.Jaroska;
                            return true;
                        }
                        lockManager.unlock(5, 24, 25); // Release [done[2], solved[18], solved[19]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Tyrs() {
                switch(random.nextInt(2)) {
                    case 0:
                        lockManager.lock(1, 5, 20, 8, 2); // Acquire [body, done[2], solved[14], solved[2], time]
                        if (done[2] == 0 && solved[14] == 0 && time >= 9 && time <= 13) { // from Tyrs to Tyrs {[done[2] = 0 and solved[14] = 0 and time >= 9 and time <= 13; done[2] = 1; solved[14] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 20, 8, 2); // Release [body, done[2], solved[14], solved[2], time]
                            currentState = Person_2Thread.States.Tyrs;
                            return true;
                        } else if(done[2] == 0 && solved[2] == 0 && time >= 1 && time <= 4) { // from Tyrs to Tyrs {[done[2] = 0 and solved[2] = 0 and time >= 1 and time <= 4; done[2] = 1; solved[2] = 1; body = body + 1]} 
                            done[2] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);
                            lockManager.unlock(1, 5, 20, 8, 2); // Release [body, done[2], solved[14], solved[2], time]
                            currentState = Person_2Thread.States.Tyrs;
                            return true;
                        }
                        lockManager.unlock(1, 5, 20, 8, 2); // Release [body, done[2], solved[14], solved[2], time]
                        return false;
                    case 1:
                        lockManager.lock(5); // Acquire [done[2]]
                        if (done[2] == 0) { // from Tyrs to Moravak {[done[2] = 0; done[2] = 1]} 
                            done[2] = (byte) (1);
                            lockManager.unlock(5); // Release [done[2]]
                            currentState = Person_2Thread.States.Moravak;
                            return true;
                        }
                        lockManager.unlock(5); // Release [done[2]]
                        return false;
                    default:
                        throw new RuntimeException("The default statement in a non-deterministic block should be unreachable!");
                }
            }

            private boolean exec_Burian() {
                lockManager.lock(5); // Acquire [done[2]]
                if (done[2] == 0) { // from Burian to Wilson {[done[2] = 0; done[2] = 1]} 
                    done[2] = (byte) (1);
                    lockManager.unlock(5); // Release [done[2]]
                    currentState = Person_2Thread.States.Wilson;
                    return true;
                }
                lockManager.unlock(5); // Release [done[2]]
                return false;
            }

            private boolean exec_Wilson() {
                lockManager.lock(0, 5); // Acquire [atmodul, done[2]]
                if (done[2] == 0) { // from Wilson to Modul {[done[2] = 0; atmodul = atmodul + 1; done[2] = 1]} 
                    atmodul = (byte) (atmodul + 1);
                    done[2] = (byte) (1);
                    lockManager.unlock(0, 5); // Release [atmodul, done[2]]
                    currentState = Person_2Thread.States.Modul;
                    return true;
                }
                lockManager.unlock(0, 5); // Release [atmodul, done[2]]
                return false;
            }

            private boolean exec_Modul() {
                // There are no transitions to be made.
                return false;
            }

            // Execute method
            private void exec() {
                boolean result;
                while(transition_counter < COUNTER_BOUND) {
                    switch(currentState) {
                        case Moravak:
                            result = exec_Moravak();
                            break;
                        case Studovna:
                            result = exec_Studovna();
                            break;
                        case Ceska:
                            result = exec_Ceska();
                            break;
                        case Svobodak:
                            result = exec_Svobodak();
                            break;
                        case Petrov:
                            result = exec_Petrov();
                            break;
                        case Spilberk:
                            result = exec_Spilberk();
                            break;
                        case Malinak:
                            result = exec_Malinak();
                            break;
                        case Jaroska:
                            result = exec_Jaroska();
                            break;
                        case Tyrs:
                            result = exec_Tyrs();
                            break;
                        case Burian:
                            result = exec_Burian();
                            break;
                        case Wilson:
                            result = exec_Wilson();
                            break;
                        case Modul:
                            result = exec_Modul();
                            break;
                        default:
                            return;
                    }

                    // Increment counter
                    transition_counter++;
                    if(result) {
                        successful_transition_counter++;
                    }
                }
                System.out.println(this.getClass().getSimpleName() + ": " + successful_transition_counter + "/" + transition_counter + " (successful/total transitions)");
            }

            // Run method
            public void run() {
                exec();
            }
        }

        // Constructor for main class
        GlobalClass(byte atmodul, byte body, byte[] done, byte[] solved, byte time) {
            // Create a lock manager.
            LockManager lockManager = new LockManager(26);

            // Instantiate global variables
            this.time = time;
            this.done = done;
            this.atmodul = atmodul;
            this.body = body;
            this.solved = solved;
            T_Timer = new GlobalClass.TimerThread(lockManager);
            T_Person_0 = new GlobalClass.Person_0Thread(lockManager);
            T_Person_1 = new GlobalClass.Person_1Thread(lockManager);
            T_Person_2 = new GlobalClass.Person_2Thread(lockManager);
        }

        // Start all threads
        public void startThreads() {
            T_Timer.start();
            T_Person_0.start();
            T_Person_1.start();
            T_Person_2.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    T_Timer.join();
                    T_Person_0.join();
                    T_Person_1.join();
                    T_Person_2.join();
                    break;
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    dve_exit_5() {
        //Instantiate the objects.
        objects = new SLCO_Class[] {
            new GlobalClass((byte) 0, (byte) 0, new byte[] {0, 0, 0}, new byte[] {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}, (byte) 0),
        };
    }

    // Start all threads
    private void startThreads() {
        for(SLCO_Class o : objects) {
            o.startThreads();
        }
    }

    // Join all threads
    private void joinThreads() {
        for(SLCO_Class o : objects) {
            o.joinThreads();
        }
    }

    // Run application
    public static void main(String[] args) {
        dve_exit_5 ap = new dve_exit_5();
        ap.startThreads();
        ap.joinThreads();
    }
}
