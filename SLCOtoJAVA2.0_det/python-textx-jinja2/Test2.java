import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class Test2 {
    // The threads
    private Java_SM3Thread java_T_SM3;

    // Global variables
    private volatile int y;

	interface Java_SM3Thread_States {
	    // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }
	}

	class Java_SM3Thread extends Thread implements Java_SM3Thread_States {
        private Thread java_t;
        private String java_threadName = "SM3Thread";

        // Current state
        private Java_SM3Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Thread local variables
        private int x;
        private boolean b;

		// Constructor
		Java_SM3Thread () {
			java_randomGenerator = new Random();
			java_currentState = Java_SM3Thread.States.SMC0;
			x = 0;
			b = true;
		}

        private boolean exec_SMC0() {
			// variable to store non-deterministic choices
			int java_choice;
			java_choice = java_randomGenerator.nextInt(3);
            switch(java_choice) {
                case 0:
                    java_currentState = Java_SM3Thread.States.SMC1;
                    return true;
                case 1:
                    if (y == 4) {
                        java_currentState = Java_SM3Thread.States.SMC1;
                        return true;
                    }
                    return false;
                case 2:
                    if (x >= 0 && x < 3) {
                        x = x + 1;
                        java_currentState = Java_SM3Thread.States.SMC1;
                        return true;
                    } else if(x == 4) {
                        x = 0;
                        java_currentState = Java_SM3Thread.States.SMC1;
                        return true;
                    }
                    return false;
            }
			return false;
        }

        private boolean exec_SMC1() {
			// variable to store non-deterministic choices
			int java_choice;
			java_currentState = Java_SM3Thread.States.SMC0;
            return true;
        }

		// Execute method
		private void exec() {
			while(true) {
			    switch(java_currentState) {
                    case SMC0:
                        exec_SMC0();
                        break;
                    case SMC1:
                        exec_SMC1();
                        break;
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
	Test2() {
		// Instantiate global variables
		y = 0;
        java_T_SM3 = new Test2.Java_SM3Thread();
	}

	// Start all threads
	private void startThreads() {
		java_T_SM3.start();
	}

	// Join all threads
	private void joinThreads() {
		while (true) {
			try {
				java_T_SM3.join();
				break;
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	// Run application
	public static void main(String[] args) {
        Test2 java_ap = new Test2();
        java_ap.startThreads();
        java_ap.joinThreads();
	}
}