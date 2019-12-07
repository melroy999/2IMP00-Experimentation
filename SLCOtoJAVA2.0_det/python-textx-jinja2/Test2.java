import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class Test2 {
    // The threads
    java_SM1Thread java_T_SM1;
    java_SM2Thread java_T_SM2;
    java_SM3Thread java_T_SM3;

    // Global variables
    public volatile int y;

	class Java_SM1Thread extends Thread {
        private Thread java_t;
        private String java_threadName = "SM1Thread";

        // Current state
        private Java_SM1Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Thread local variables
        private int[] x;

        // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }

		// Constructor
		Java_SM1Thread () {
			java_randomGenerator = new Random();
			java_currentState = Test2.java_State.;
			x = new int[] {0, 0};
		}


        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			(Decision.N_DET, [SMC0->SMC1[(x[0] <= 3)], (Decision.DET, [SMC0->SMC1[(x[1] = 2)], SMC0->SMC1[(x[1] = 3)]]), (Decision.DET, [(Decision.N_DET, [SMC0->SMC1[(x[0] = 0)], SMC0->SMC1[(x[0] = 0)]]), SMC0->SMC1[(x[0] = 1)]])])
        }
        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			None
        }

		// Execute method
		public void exec() {
			while(true) {
			    switch(java_currentState) {
                    case :
                        exec_();
                        break;
                    case :
                        exec_();
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

	class Java_SM2Thread extends Thread {
        private Thread java_t;
        private String java_threadName = "SM2Thread";

        // Current state
        private Java_SM2Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Thread local variables
        private int[] x;

        // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }

		// Constructor
		Java_SM2Thread () {
			java_randomGenerator = new Random();
			java_currentState = Test2.java_State.;
			x = new int[] {0, 0};
		}


        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			(Decision.N_DET, [SMC0->SMC1[(x[0] <= 3)], (Decision.DET, [SMC0->SMC1[((x[0] mod 4) = 0)], SMC0->SMC1[((x[0] mod 4) = 1)], SMC0->SMC1[((x[0] mod 4) = 2)], SMC0->SMC1[((x[0] mod 4) = 3)]])])
        }
        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			None
        }

		// Execute method
		public void exec() {
			while(true) {
			    switch(java_currentState) {
                    case :
                        exec_();
                        break;
                    case :
                        exec_();
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

	class Java_SM3Thread extends Thread {
        private Thread java_t;
        private String java_threadName = "SM3Thread";

        // Current state
        private Java_SM3Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Thread local variables
        private int x;
        private boolean b;

        // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }

		// Constructor
		Java_SM3Thread () {
			java_randomGenerator = new Random();
			java_currentState = Test2.java_State.;
			x = 0;
			b = true;
		}


        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			(Decision.N_DET, [SMC0->SMC1[(y = 4)], SMC0->SMC1[(b or (! b))], (Decision.DET, [SMC0->SMC1[((x >= 0) and (x < 3))], SMC0->SMC1[(x = 4)]])])
        }
        private void exec_() {
			// variable to store non-deterministic choices
			int java_choice;

			None
        }

		// Execute method
		public void exec() {
			while(true) {
			    switch(java_currentState) {
                    case :
                        exec_();
                        break;
                    case :
                        exec_();
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
	}

	// Start all threads
	public void startThreads() {
		java_T_SM1.start();
		java_T_SM2.start();
		java_T_SM3.start();
	}

	// Join all threads
	public void joinThreads() {
		while (true) {
			try {
				java_T_SM1.join();
				java_T_SM2.join();
				java_T_SM3.join();
				break;
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}

	// Run application
	public static void main(String args[]) {
        Test2 java_ap = new Test2();
        java_ap.startThreads();
        java_ap.joinThreads();
	}
}