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
    public volatile  ;

	class java_SM1Thread extends Thread {
		private Thread java_t;
		private String java_threadName = "SM1Thread";
		// Current state
		private Test2.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Thread local variables
		private <__main__.Type object at 0x000001D71FD9B470> x;

		// Constructor
		java_SM1Thread () {
			java_randomGenerator = new Random();
			x = new <__main__.Variable object at 0x000001D71FD9B4A8> <__main__.Variable object at 0x000001D71FD9B4A8>;
		}

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
			while(true) {
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
	class java_SM2Thread extends Thread {
		private Thread java_t;
		private String java_threadName = "SM2Thread";
		// Current state
		private Test2.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Thread local variables
		private <__main__.Type object at 0x000001D71FDB7B00> x;

		// Constructor
		java_SM2Thread () {
			java_randomGenerator = new Random();
			x = new <__main__.Variable object at 0x000001D71FDB7B38> <__main__.Variable object at 0x000001D71FDB7B38>;
		}

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
			while(true) {
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
	class java_SM3Thread extends Thread {
		private Thread java_t;
		private String java_threadName = "SM3Thread";
		// Current state
		private Test2.java_State java_currentState;
		// Random number generator to handle non-determinism
		private Random java_randomGenerator;
		// Thread local variables
		private <__main__.Type object at 0x000001D71FDC9E80> x;
		private <__main__.Type object at 0x000001D71FDC9F60> b;

		// Constructor
		java_SM3Thread () {
			java_randomGenerator = new Random();
			x = <__main__.Variable object at 0x000001D71FDC9EB8>;
			b = <__main__.Variable object at 0x000001D71FDC9F98>;
		}

		// Execute method
		public void exec() {
			// variable to store non-deterministic choices
			int java_choice;
			while(true) {
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
		y = <__main__.Variable object at 0x000001D71FDD10B8>;
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