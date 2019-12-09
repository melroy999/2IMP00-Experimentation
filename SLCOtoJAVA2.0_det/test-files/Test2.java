import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class Test2 {
    // The threads
    private Java_SM3Thread java_T_SM3;
    private Java_SM1Thread java_T_SM1;
    private Java_SM2Thread java_T_SM2;

    // Upperbound for transition counter
    private static final long java_COUNTER_BOUND = 300000000L;

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

        // Current state
        private Java_SM3Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Counter of main while-loop iterations
        long java_transition_counter;

        // Thread local variables
        private int x;
        private boolean b;

		// Constructor
		Java_SM3Thread () {
			java_randomGenerator = new Random();
			java_transition_counter = 0;
			java_currentState = Java_SM3Thread.States.SMC0;
			x = 0;
			b = true;
		}

        private boolean exec_SMC0() {
			switch(java_randomGenerator.nextInt(3)) {
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
			y = y + 1;

            java_currentState = Java_SM3Thread.States.SMC0;
            return true;
        }

		// Execute method
		private void exec() {
		    boolean result = false;
			while(java_transition_counter < java_COUNTER_BOUND) {
			    switch(java_currentState) {
                    case SMC0:
                        result = exec_SMC0();
                        break;
                    case SMC1:
                        result = exec_SMC1();
                        break;
                    default:
						return;
			    }

                // Increment counter
                if(result) {
                    java_transition_counter++;
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
				java_t = new Thread(this, "SM3Thread");
				java_t.start();
			}
		}
	}

	interface Java_SM1Thread_States {
	    // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }
	}

	class Java_SM1Thread extends Thread implements Java_SM1Thread_States {
        private Thread java_t;

        // Current state
        private Java_SM1Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Counter of main while-loop iterations
        long java_transition_counter;

        // Thread local variables
        private int[] x;

		// Constructor
		Java_SM1Thread () {
			java_randomGenerator = new Random();
			java_transition_counter = 0;
			java_currentState = Java_SM1Thread.States.SMC0;
			x = new int[] {0, 0};
		}

        private boolean exec_SMC0() {
			switch(java_randomGenerator.nextInt(3)) {
                case 0:
                    if (x[0] <= 3) {
                        java_currentState = Java_SM1Thread.States.SMC1;
                        return true;
                    }
                    return false;
                case 1:
                    if (((x[0] == 0)) || ((x[0] == 0))) {
                        switch(java_randomGenerator.nextInt(2)) {
                            case 0:
                                if (x[0] == 0) {
                                    if(!(x[0] == 0)) return false;
                                    x[0] = 0;
                                    y = y + 1;

                                    java_currentState = Java_SM1Thread.States.SMC1;
                                    return true;
                                }
                                return false;
                            case 1:
                                if (x[0] == 0) {
                                    if(!(x[0] == 0)) return false;
                                    y = y + 1;

                                    java_currentState = Java_SM1Thread.States.SMC1;
                                    return true;
                                }
                                return false;
                        }
                    } else if(x[0] == 1) {
                        java_currentState = Java_SM1Thread.States.SMC1;
                        return true;
                    }
                    return false;
                case 2:
                    if (x[1] == 3) {
                        java_currentState = Java_SM1Thread.States.SMC1;
                        return true;
                    } else if(x[1] == 2) {
                        java_currentState = Java_SM1Thread.States.SMC1;
                        return true;
                    }
                    return false;
            }
			return false;
        }

        private boolean exec_SMC1() {
			return false;
        }

		// Execute method
		private void exec() {
		    boolean result = false;
			while(java_transition_counter < java_COUNTER_BOUND) {
			    switch(java_currentState) {
                    case SMC0:
                        result = exec_SMC0();
                        break;
                    case SMC1:
                        result = exec_SMC1();
                        break;
                    default:
						return;
			    }

                // Increment counter
                if(result) {
                    java_transition_counter++;
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
				java_t = new Thread(this, "SM1Thread");
				java_t.start();
			}
		}
	}

	interface Java_SM2Thread_States {
	    // Enum type for state machine states
        enum States {
            SMC0, SMC1
        }
	}

	class Java_SM2Thread extends Thread implements Java_SM2Thread_States {
        private Thread java_t;

        // Current state
        private Java_SM2Thread.States java_currentState;

        // Random number generator to handle non-determinism
        private Random java_randomGenerator;

        // Counter of main while-loop iterations
        long java_transition_counter;

        // Thread local variables
        private int[] x;

		// Constructor
		Java_SM2Thread () {
			java_randomGenerator = new Random();
			java_transition_counter = 0;
			java_currentState = Java_SM2Thread.States.SMC0;
			x = new int[] {0, 0};
		}

        private boolean exec_SMC0() {
			switch(java_randomGenerator.nextInt(2)) {
                case 0:
                    if (x[0] <= 3) {
                        java_currentState = Java_SM2Thread.States.SMC1;
                        return true;
                    }
                    return false;
                case 1:
                    if (x[0] % 4 == 0) {
                        java_currentState = Java_SM2Thread.States.SMC1;
                        return true;
                    } else if(x[0] % 4 == 1) {
                        java_currentState = Java_SM2Thread.States.SMC1;
                        return true;
                    } else if(x[0] % 4 == 2) {
                        java_currentState = Java_SM2Thread.States.SMC1;
                        return true;
                    } else if(x[0] % 4 == 3) {
                        java_currentState = Java_SM2Thread.States.SMC1;
                        return true;
                    }
                    return false;
            }
			return false;
        }

        private boolean exec_SMC1() {
			return false;
        }

		// Execute method
		private void exec() {
		    boolean result = false;
			while(java_transition_counter < java_COUNTER_BOUND) {
			    switch(java_currentState) {
                    case SMC0:
                        result = exec_SMC0();
                        break;
                    case SMC1:
                        result = exec_SMC1();
                        break;
                    default:
						return;
			    }

                // Increment counter
                if(result) {
                    java_transition_counter++;
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
				java_t = new Thread(this, "SM2Thread");
				java_t.start();
			}
		}
	}

	// Constructor for main class
	Test2() {
		// Instantiate global variables
		y = 0;
        java_T_SM3 = new Test2.Java_SM3Thread();
        java_T_SM1 = new Test2.Java_SM1Thread();
        java_T_SM2 = new Test2.Java_SM2Thread();
	}

	// Start all threads
	private void startThreads() {
		java_T_SM3.start();
		java_T_SM1.start();
		java_T_SM2.start();
	}

	// Join all threads
	private void joinThreads() {
		while (true) {
			try {
				java_T_SM3.join();
				java_T_SM1.join();
				java_T_SM2.join();
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