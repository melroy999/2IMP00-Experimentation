import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;
import java.util.HashMap;
import java.time.Duration;
import java.time.Instant;

// main class
public class TestSimple {
  // The threads
  java_SM1Thread java_T_SM1;

  // Upperbound for transition counter
  public static final long java_COUNTER_BOUND = 10000000L;

  // Enum type for state machine states
  public enum java_State {
  SM1_0, SM1_1
  }

  // Global variables
  public volatile int y;
  public volatile int[] x;

	// Lock class to handle locks of global variables
	class java_Keeper {
    // The locks
    ReentrantLock[] locks;
    // Which locks need to be acquired?
    boolean[] lockneeded;

		// Constructor
		java_Keeper() {
			locks = new ReentrantLock[3];
			lockneeded = new boolean[] { true,true,true };
			for (int i = 0; i < 3; i++) {
				locks[i] = new ReentrantLock(true);
			}
		}

		// Lock method
		public void lock(int[] l, int size) {
			for (int i = 0; i < size; i++) {
				if (lockneeded[l[i]]) {
          			locks[l[i]].lock();
        		}
      		}
		}

		// Unlock method
		public void unlock(int[] l, int size) {
			for (int i = 0; i < size; i++) {
				if (lockneeded[l[i]]) {
          			locks[l[i]].unlock();
        		}
      		}
		}
	}

	class java_SM1Thread extends Thread {
		private Thread java_t;
		private String java_threadName = "SM1Thread";
		// Current state
		private TestSimple.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Counter of main while-loop iterations
		long java_transcounter;
		// Counter of main while-loop iterations that are successful
		long java_successful_transcounter;
        // A counter for the transitions.
        private HashMap<String, Integer> transitionCounterMap;
		// Keeper of global variables
		private TestSimple.java_Keeper java_kp;
		// Array to store IDs of locks to be acquired
		private int[] java_lockIDs;
		// Thread local variables

		// Constructor
		java_SM1Thread (TestSimple.java_Keeper java_k) {
			java_randomGenerator = new Random();
			java_transcounter = 0;
			java_currentState = TestSimple.java_State.SM1_0;
            java_kp = java_k;
            java_lockIDs = new int[2];
            transitionCounterMap = new HashMap<>();
		}

		// Transition functions
        
        boolean execute_SM1_0_0() {
          // [y <= 10; y := y + 1]
          //System.out.println("SM1_SM1_0_0");
          java_lockIDs[0] = 2;
          //System.out.println("SM1_SM1_0__sort");
          Arrays.sort(java_lockIDs,0,1);
          //System.out.println("SM1_SM1_0__lock");
          java_kp.lock(java_lockIDs, 1);
          if (!(y <= 10)) { java_kp.unlock(java_lockIDs, 1); java_transcounter++; return false; }
          y = y + 1;
          //System.out.println("SM1_SM1_0__unlock");
          java_kp.unlock(java_lockIDs, 1);
          transitionCounterMap.merge("from SM1_0 to SM1_1 {[y <= 10; y := y + 1]}", 1, Integer::sum);
          return true;
        }
        
        boolean execute_SM1_0_1() {
          // [y > 10; x[0] := 0; y := 0]
          //System.out.println("SM1_SM1_0_0");
          java_lockIDs[0] = 0 + 0;
          //System.out.println("SM1_SM1_0_1");
          java_lockIDs[1] = 2;
          //System.out.println("SM1_SM1_0__sort");
          Arrays.sort(java_lockIDs,0,2);
          //System.out.println("SM1_SM1_0__lock");
          java_kp.lock(java_lockIDs, 2);
          if (!(y > 10)) { java_kp.unlock(java_lockIDs, 2); java_transcounter++; return false; }
          x[0] = 0;
          y = 0;
          //System.out.println("SM1_SM1_0__unlock");
          java_kp.unlock(java_lockIDs, 2);
          transitionCounterMap.merge("from SM1_0 to SM1_1 {[y > 10; x[0] := 0; y := 0]}", 1, Integer::sum);
          return true;
        }
        
        boolean execute_SM1_1_0() {
          // x[0] := x[0] + 1
          //System.out.println("SM1_SM1_1_0");
          java_lockIDs[0] = 0 + 0;
          //System.out.println("SM1_SM1_1__sort");
          Arrays.sort(java_lockIDs,0,1);
          //System.out.println("SM1_SM1_1__lock");
          java_kp.lock(java_lockIDs, 1);
          x[0] = x[0] + 1;
          //System.out.println("SM1_SM1_1__unlock");
          java_kp.unlock(java_lockIDs, 1);
          transitionCounterMap.merge("from SM1_1 to SM1_0 {x[0] := x[0] + 1}", 1, Integer::sum);
          return true;
        }

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
            Instant start = Instant.now();
			while(java_transcounter < java_COUNTER_BOUND) {
				//System.out.println(java_transcounter);
				switch(java_currentState) {
					case SM1_0:
						//System.out.println("SM1_SM1_0 " + java_transcounter);
						java_choice = java_randomGenerator.nextInt(2);
						switch(java_choice) {
							case 0:
								//System.out.println("SM1_SM1_0_0");
								if (execute_SM1_0_0()) {
								  // Change state
								  //System.out.println("SM1_SM1_0_0_changestate");
								  java_currentState = TestSimple.java_State.SM1_1;
								  // Increment counter
								  //System.out.println("SM1_SM1_0_0_increment");
								  java_successful_transcounter++;
								}
								break;
							case 1:
								//System.out.println("SM1_SM1_0_1");
								if (execute_SM1_0_1()) {
								  // Change state
								  //System.out.println("SM1_SM1_0_1_changestate");
								  java_currentState = TestSimple.java_State.SM1_1;
								  // Increment counter
								  //System.out.println("SM1_SM1_0_1_increment");
								  java_successful_transcounter++;
								}
								break;
						}
						break;
					case SM1_1:
						//System.out.println("SM1_SM1_1 " + java_transcounter);
                        if (execute_SM1_1_0()) {
						  // Change state
						  java_currentState = TestSimple.java_State.SM1_0;
						  // Increment counter
						  java_successful_transcounter++;
						}
						break;
					default:
						return;
				}
                // Increment counter
                java_transcounter++;
			}
            System.out.println("P.SM1: " + java_successful_transcounter + "/" + java_transcounter + " (successful/total transitions)");
            Instant finish = Instant.now();
            System.out.println("Thread P.SM1 finished after " + Duration.between(start, finish).toMillis() + " milliseconds.");
            System.out.println("Transition count:");
            transitionCounterMap.forEach((key, value) -> System.out.println(key + ", " + value));
            System.out.println();
		}

		// Run method
		public void run() {
			exec();
		}
	}

	// Constructor for main class
	TestSimple() {
		// Instantiate global variables
		y = 0;
		x = new int[] {0,0};
		TestSimple.java_Keeper java_k = new TestSimple.java_Keeper();
		java_T_SM1 = new TestSimple.java_SM1Thread(java_k);
	}

	// Start all threads
	public void startThreads() {
		java_T_SM1.start();
	}

	// Join all threads
	public void joinThreads() {
		while (true) {
			try {
				java_T_SM1.join();
				break;
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	// Run application
	public static void main(String args[]) {
    TestSimple java_ap = new TestSimple();
    java_ap.startThreads();
    java_ap.joinThreads();
	}
}