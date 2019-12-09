import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class Test {
  // The threads
  java_SM1Thread java_T_SM1;
  java_ComThread java_T_Com;

  // Enum type for state machine states
  public enum java_State {
  SMC1, Com2, Com0, SMC0, Com1
  }

  // Global variables
  public volatile boolean[] x;
  public volatile int y;

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
		private Test.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Keeper of global variables
		private Test.java_Keeper java_kp;
		// Array to store IDs of locks to be acquired
		private int[] java_lockIDs;
		// Thread local variables
		private int i;

		// Constructor
		java_SM1Thread (Test.java_Keeper java_k) {
			java_randomGenerator = new Random();
			java_currentState = Test.java_State.SMC0;
            java_kp = java_k;
            java_lockIDs = new int[3];
			i = 0;
		}

		// Transition functions
        
        boolean execute_SMC0_0() {
          // [not x[i]; i := i + 1; x[i] := i = 2; i := 3; x[0] := False]
          //System.out.println("SM1_SMC0_0");
          java_lockIDs[0] = 0 + (i + 1);
          //System.out.println("SM1_SMC0_1");
          java_lockIDs[1] = 0 + 0;
          //System.out.println("SM1_SMC0_2");
          java_lockIDs[2] = 0 + i;
          //System.out.println("SM1_SMC0__sort");
          Arrays.sort(java_lockIDs,0,3);
          //System.out.println("SM1_SMC0__lock");
          java_kp.lock(java_lockIDs, 3);
          if (!(!(x[i]))) { java_kp.unlock(java_lockIDs, 3); return false; }
          i = i + 1;
          x[i] = i == 2;
          i = 3;
          x[0] = false;
          //System.out.println("SM1_SMC0__unlock");
          java_kp.unlock(java_lockIDs, 3);
          return true;
        }
        
        boolean execute_SMC0_1() {
          // i := 0
          i = 0;
          return true;
        }

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
			while(true) {
				switch(java_currentState) {
					case SMC0:
						java_choice = java_randomGenerator.nextInt(2);
						switch(java_choice) {
							case 0:
								//System.out.println("SM1_SMC0_0");
								if (execute_SMC0_0()) {
								  // Change state
								  //System.out.println("SM1_SMC0_0_changestate");
								  java_currentState = Test.java_State.SMC1;
								}
								break;
							case 1:
								//System.out.println("SM1_SMC0_1");
								if (execute_SMC0_1()) {
								  // Change state
								  //System.out.println("SM1_SMC0_1_changestate");
								  java_currentState = Test.java_State.SMC0;
								}
								break;
						}
					default:
						return;
				}
			}
		}

		// Run method
		public void run() {
			exec();
		}

		// Start method
		public void start() {
			if (java_t == null) {
				java_t = new Thread(this);
				java_t.start();
			}
		}
	}
	class java_ComThread extends Thread {
		private Thread java_t;
		private String java_threadName = "ComThread";
		// Current state
		private Test.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Keeper of global variables
		private Test.java_Keeper java_kp;
		// Array to store IDs of locks to be acquired
		private int[] java_lockIDs;
		// Thread local variables
		private int lx;

		// Constructor
		java_ComThread (Test.java_Keeper java_k) {
			java_randomGenerator = new Random();
			java_currentState = Test.java_State.Com0;
            java_kp = java_k;
            java_lockIDs = new int[0];
			lx = 0;
		}

		// Transition functions
        
        boolean execute_Com0_0() {
          // lx = 0
          if (!(lx == 0)) { return false; }
          return true;
        }

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
			while(true) {
				switch(java_currentState) {
					case Com0:
                        if (execute_Com0_0()) {
						  // Change state
						  java_currentState = Test.java_State.Com1;
						}
						break;
					default:
						return;
				}
			}
		}

		// Run method
		public void run() {
			exec();
		}

		// Start method
		public void start() {
			if (java_t == null) {
				java_t = new Thread(this);
				java_t.start();
			}
		}
	}

	// Constructor for main class
	Test() {
		// Instantiate global variables
		x = new boolean[] {false,true};
		y = 0;
		Test.java_Keeper java_k = new Test.java_Keeper();
		java_T_SM1 = new Test.java_SM1Thread(java_k);
		java_T_Com = new Test.java_ComThread(java_k);
	}

	// Start all threads
	public void startThreads() {
		java_T_SM1.start();
		java_T_Com.start();
	}

	// Join all threads
	public void joinThreads() {
		while (true) {
			try {
				java_T_SM1.join();
				java_T_Com.join();
				break;
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	// Run application
	public static void main(String args[]) {
    Test java_ap = new Test();
    java_ap.startThreads();
    java_ap.joinThreads();
	}
}