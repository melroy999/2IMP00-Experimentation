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
			java_currentState = Test2.java_State.SMC0;
			x = new int[] {0, 0};
		}

        private boolean exec_SMC0() {
			// variable to store non-deterministic choices
			int java_choice;
			java_choice = java_randomGenerator.nextInt(3);
            switch(java_choice) {
                case 0:
                    if (x[0] <= 3) {
                        return true;
                    } else {
                        return false;
                    }
                case 1:
                    if (((x[0] == 0)) || ((x[0] == 0))) {
                        java_choice = java_randomGenerator.nextInt(2);
                        switch(java_choice) {
                            case 0:
                                if (x[0] == 0) {
                                    return true;
                                } else {
                                    return false;
                                }
                            case 1:
                                if (x[0] == 0) {
                                    x[0] = 0;
                                    return true;
                                } else {
                                    return false;
                                }
                        }
                    } else if(x[0] == 1) {
                        return true;
                    } else {
                        return false;
                    }
                case 2:
                    if (x[1] == 3) {
                        return true;
                    } else if(x[1] == 2) {
                        return true;
                    } else {
                        return false;
                    }
            }
        }

        private boolean exec_SMC1() {
			// variable to store non-deterministic choices
			return false;
        }

		// Execute method
		public void exec() {
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
			java_currentState = Test2.java_State.SMC0;
			x = new int[] {0, 0};
		}

        private boolean exec_SMC0() {
			// variable to store non-deterministic choices
			int java_choice;
			java_choice = java_randomGenerator.nextInt(2);
            switch(java_choice) {
                case 0:
                    if (x[0] <= 3) {
                        return true;
                    } else {
                        return false;
                    }
                case 1:
                    if (x[0] % 4 == 0) {
                        return true;
                    } else if(x[0] % 4 == 1) {
                        return true;
                    } else if(x[0] % 4 == 2) {
                        return true;
                    } else if(x[0] % 4 == 3) {
                        return true;
                    } else {
                        return false;
                    }
            }
        }

        private boolean exec_SMC1() {
			// variable to store non-deterministic choices
			return false;
        }

		// Execute method
		public void exec() {
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
			java_currentState = Test2.java_State.SMC0;
			x = 0;
			b = true;
		}

        private boolean exec_SMC0() {
			// variable to store non-deterministic choices
			int java_choice;
			java_choice = java_randomGenerator.nextInt(3);
            switch(java_choice) {
                case 0:
                    if ( == 4) {
                        return true;
                    } else {
                        return false;
                    }
                case 1:
                    if ( || not ()) {
                        return true;
                    } else {
                        return false;
                    }
                case 2:
                    if ( >= 0 &&  < 3) {
                        return true;
                    } else if( == 4) {
                        return true;
                    } else {
                        return false;
                    }
            }
        }

        private boolean exec_SMC1() {
			// variable to store non-deterministic choices
			return false;
        }

		// Execute method
		public void exec() {
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