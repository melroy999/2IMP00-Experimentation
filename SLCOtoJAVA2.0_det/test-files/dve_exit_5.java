import java.util.Random;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Arrays;

// main class
public class dve_exit_5 {
    // The objects in the model.
    private final SLCO_Class[] objects;

    // Upperbound for transition counter
    private static final long java_COUNTER_BOUND = 300000000L;

    interface SLCO_Class {
        void startThreads();
        void joinThreads();
    }

    // representation of a class
    public static class GlobalClass implements SLCO_Class {
        // The threads
        private Java_TimerThread java_T_Timer;
        private Java_Person_0Thread java_T_Person_0;
        private Java_Person_1Thread java_T_Person_1;
        private Java_Person_2Thread java_T_Person_2;

        // Global variables
        private volatile byte time;
        private volatile byte[] done;
        private volatile byte atmodul;
        private volatile byte body;
        private volatile byte[] solved;

        interface Java_GlobalClass_TimerThread_States {
            enum States {
                q
            }
        }

        class Java_TimerThread extends Thread implements Java_GlobalClass_TimerThread_States {
            private Thread java_t;

            // Current state
            private Java_TimerThread.States java_currentState;

            // Random number generator to handle non-determinism
            private Random java_randomGenerator;

            // Counter of main while-loop iterations
            long java_transition_counter;

            // Constructor
            Java_TimerThread () {
                java_randomGenerator = new Random();
                java_transition_counter = 0;
                java_currentState = Java_TimerThread.States.q;
            }

            private boolean exec_q() {
                if (time < 6) {
                    if(!(time < 6)) return false;
                    done[0] = (byte) (0);
                    done[1] = (byte) (0);
                    done[2] = (byte) (0);
                    time = (byte) (time + 1);

                    java_currentState = Java_TimerThread.States.q;
                    return true;
                }
                return false;
            }

            // Execute method
            private void exec() {
                boolean result = false;
                while(java_transition_counter < java_COUNTER_BOUND) {
                    switch(java_currentState) {
                        case q:
                            result = exec_q();
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
                    java_t = new Thread(this, "TimerThread");
                    java_t.start();
                }
            }
        }

        interface Java_GlobalClass_Person_0Thread_States {
            enum States {
                Studovna, Moravak, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Java_Person_0Thread extends Thread implements Java_GlobalClass_Person_0Thread_States {
            private Thread java_t;

            // Current state
            private Java_Person_0Thread.States java_currentState;

            // Random number generator to handle non-determinism
            private Random java_randomGenerator;

            // Counter of main while-loop iterations
            long java_transition_counter;

            // Constructor
            Java_Person_0Thread () {
                java_randomGenerator = new Random();
                java_transition_counter = 0;
                java_currentState = Java_Person_0Thread.States.Studovna;
            }

            private boolean exec_Studovna() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0 && solved[3] == 0 && time >= 2 && time <= 6) {
                            if(!(done[0] == 0 && solved[3] == 0 && time >= 2 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[0] == 0 && solved[6] == 0 && time >= 3 && time <= 6) {
                            if(!(done[0] == 0 && solved[6] == 0 && time >= 3 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[0] == 0 && solved[10] == 0 && time >= 6 && time <= 6) {
                            if(!(done[0] == 0 && solved[10] == 0 && time >= 6 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Moravak() {
                switch(java_randomGenerator.nextInt(7)) {
                    case 0:
                        if (done[0] == 0 && solved[19] == 1 && solved[17] == 1) {
                            if(!(done[0] == 0 && solved[19] == 1 && solved[17] == 1)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Burian;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (solved[16] == 1 && done[0] == 0) {
                            if(!(solved[16] == 1 && done[0] == 0)) return false;
                            done[0] = (byte) (1);
                            solved[18] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 6:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Ceska() {
                return false;
            }

            private boolean exec_Svobodak() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (body >= 10 && done[0] == 0) {
                            if(!(body >= 10 && done[0] == 0)) return false;
                            done[0] = (byte) (1);
                            solved[17] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[0] == 0 && solved[5] == 0 && time >= 5 && time <= 5) {
                            if(!(done[0] == 0 && solved[5] == 0 && time >= 5 && time <= 5)) return false;
                            done[0] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        } else if(done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Petrov() {
                switch(java_randomGenerator.nextInt(4)) {
                    case 0:
                        if (body >= 10 && done[0] == 0) {
                            if(!(body >= 10 && done[0] == 0)) return false;
                            done[0] = (byte) (1);
                            solved[16] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[0] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Petrov;
                            return true;
                        } else if(done[0] == 0 && solved[4] == 0 && time >= 5 && time <= 5) {
                            if(!(done[0] == 0 && solved[4] == 0 && time >= 5 && time <= 5)) return false;
                            done[0] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Petrov;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Spilberk() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0 && solved[1] == 0 && time >= 0 && time <= 4) {
                            if(!(done[0] == 0 && solved[1] == 0 && time >= 0 && time <= 4)) return false;
                            done[0] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Spilberk;
                            return true;
                        } else if(done[0] == 0 && solved[8] == 0 && time >= 8 && time <= 9) {
                            if(!(done[0] == 0 && solved[8] == 0 && time >= 8 && time <= 9)) return false;
                            done[0] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Malinak() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[0] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[0] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Jaroska() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[0] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[0] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 1:
                        if (solved[18] == 1 && done[0] == 0) {
                            if(!(solved[18] == 1 && done[0] == 0)) return false;
                            done[0] = (byte) (1);
                            solved[19] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Tyrs() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[0] == 0) {
                            if(!(done[0] == 0)) return false;
                            done[0] = (byte) (1);

                            java_currentState = Java_Person_0Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[0] == 0 && solved[2] == 0 && time >= 1 && time <= 4) {
                            if(!(done[0] == 0 && solved[2] == 0 && time >= 1 && time <= 4)) return false;
                            done[0] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Tyrs;
                            return true;
                        } else if(done[0] == 0 && solved[14] == 0 && time >= 9 && time <= 13) {
                            if(!(done[0] == 0 && solved[14] == 0 && time >= 9 && time <= 13)) return false;
                            done[0] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_0Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Burian() {
                if (done[0] == 0) {
                    if(!(done[0] == 0)) return false;
                    done[0] = (byte) (1);

                    java_currentState = Java_Person_0Thread.States.Wilson;
                    return true;
                }
                return false;
            }

            private boolean exec_Wilson() {
                if (done[0] == 0) {
                    if(!(done[0] == 0)) return false;
                    atmodul = (byte) (atmodul + 1);
                    done[0] = (byte) (1);

                    java_currentState = Java_Person_0Thread.States.Modul;
                    return true;
                }
                return false;
            }

            private boolean exec_Modul() {
                return false;
            }

            // Execute method
            private void exec() {
                boolean result = false;
                while(java_transition_counter < java_COUNTER_BOUND) {
                    switch(java_currentState) {
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
                    java_t = new Thread(this, "Person_0Thread");
                    java_t.start();
                }
            }
        }

        interface Java_GlobalClass_Person_1Thread_States {
            enum States {
                Moravak, Studovna, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Java_Person_1Thread extends Thread implements Java_GlobalClass_Person_1Thread_States {
            private Thread java_t;

            // Current state
            private Java_Person_1Thread.States java_currentState;

            // Random number generator to handle non-determinism
            private Random java_randomGenerator;

            // Counter of main while-loop iterations
            long java_transition_counter;

            // Constructor
            Java_Person_1Thread () {
                java_randomGenerator = new Random();
                java_transition_counter = 0;
                java_currentState = Java_Person_1Thread.States.Moravak;
            }

            private boolean exec_Moravak() {
                switch(java_randomGenerator.nextInt(7)) {
                    case 0:
                        if (done[1] == 0 && solved[19] == 1 && solved[17] == 1) {
                            if(!(done[1] == 0 && solved[19] == 1 && solved[17] == 1)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Burian;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (solved[16] == 1 && done[1] == 0) {
                            if(!(solved[16] == 1 && done[1] == 0)) return false;
                            done[1] = (byte) (1);
                            solved[18] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 6:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Studovna() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0 && solved[3] == 0 && time >= 2 && time <= 6) {
                            if(!(done[1] == 0 && solved[3] == 0 && time >= 2 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[1] == 0 && solved[6] == 0 && time >= 3 && time <= 6) {
                            if(!(done[1] == 0 && solved[6] == 0 && time >= 3 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[1] == 0 && solved[10] == 0 && time >= 6 && time <= 6) {
                            if(!(done[1] == 0 && solved[10] == 0 && time >= 6 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Ceska() {
                return false;
            }

            private boolean exec_Svobodak() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (body >= 10 && done[1] == 0) {
                            if(!(body >= 10 && done[1] == 0)) return false;
                            done[1] = (byte) (1);
                            solved[17] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[1] == 0 && solved[5] == 0 && time >= 5 && time <= 5) {
                            if(!(done[1] == 0 && solved[5] == 0 && time >= 5 && time <= 5)) return false;
                            done[1] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        } else if(done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Petrov() {
                switch(java_randomGenerator.nextInt(4)) {
                    case 0:
                        if (body >= 10 && done[1] == 0) {
                            if(!(body >= 10 && done[1] == 0)) return false;
                            done[1] = (byte) (1);
                            solved[16] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[1] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Petrov;
                            return true;
                        } else if(done[1] == 0 && solved[4] == 0 && time >= 5 && time <= 5) {
                            if(!(done[1] == 0 && solved[4] == 0 && time >= 5 && time <= 5)) return false;
                            done[1] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Petrov;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Spilberk() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0 && solved[1] == 0 && time >= 0 && time <= 4) {
                            if(!(done[1] == 0 && solved[1] == 0 && time >= 0 && time <= 4)) return false;
                            done[1] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Spilberk;
                            return true;
                        } else if(done[1] == 0 && solved[8] == 0 && time >= 8 && time <= 9) {
                            if(!(done[1] == 0 && solved[8] == 0 && time >= 8 && time <= 9)) return false;
                            done[1] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Malinak() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[1] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[1] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Jaroska() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[1] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[1] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 1:
                        if (solved[18] == 1 && done[1] == 0) {
                            if(!(solved[18] == 1 && done[1] == 0)) return false;
                            done[1] = (byte) (1);
                            solved[19] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Tyrs() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[1] == 0) {
                            if(!(done[1] == 0)) return false;
                            done[1] = (byte) (1);

                            java_currentState = Java_Person_1Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[1] == 0 && solved[2] == 0 && time >= 1 && time <= 4) {
                            if(!(done[1] == 0 && solved[2] == 0 && time >= 1 && time <= 4)) return false;
                            done[1] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Tyrs;
                            return true;
                        } else if(done[1] == 0 && solved[14] == 0 && time >= 9 && time <= 13) {
                            if(!(done[1] == 0 && solved[14] == 0 && time >= 9 && time <= 13)) return false;
                            done[1] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_1Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Burian() {
                if (done[1] == 0) {
                    if(!(done[1] == 0)) return false;
                    done[1] = (byte) (1);

                    java_currentState = Java_Person_1Thread.States.Wilson;
                    return true;
                }
                return false;
            }

            private boolean exec_Wilson() {
                if (done[1] == 0) {
                    if(!(done[1] == 0)) return false;
                    atmodul = (byte) (atmodul + 1);
                    done[1] = (byte) (1);

                    java_currentState = Java_Person_1Thread.States.Modul;
                    return true;
                }
                return false;
            }

            private boolean exec_Modul() {
                return false;
            }

            // Execute method
            private void exec() {
                boolean result = false;
                while(java_transition_counter < java_COUNTER_BOUND) {
                    switch(java_currentState) {
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
                    java_t = new Thread(this, "Person_1Thread");
                    java_t.start();
                }
            }
        }

        interface Java_GlobalClass_Person_2Thread_States {
            enum States {
                Moravak, Studovna, Ceska, Svobodak, Petrov, Spilberk, Malinak, Jaroska, Tyrs, Burian, Wilson, Modul
            }
        }

        class Java_Person_2Thread extends Thread implements Java_GlobalClass_Person_2Thread_States {
            private Thread java_t;

            // Current state
            private Java_Person_2Thread.States java_currentState;

            // Random number generator to handle non-determinism
            private Random java_randomGenerator;

            // Counter of main while-loop iterations
            long java_transition_counter;

            // Constructor
            Java_Person_2Thread () {
                java_randomGenerator = new Random();
                java_transition_counter = 0;
                java_currentState = Java_Person_2Thread.States.Moravak;
            }

            private boolean exec_Moravak() {
                switch(java_randomGenerator.nextInt(7)) {
                    case 0:
                        if (done[2] == 0 && solved[19] == 1 && solved[17] == 1) {
                            if(!(done[2] == 0 && solved[19] == 1 && solved[17] == 1)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Burian;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (solved[16] == 1 && done[2] == 0) {
                            if(!(solved[16] == 1 && done[2] == 0)) return false;
                            done[2] = (byte) (1);
                            solved[18] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 6:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Studovna() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0 && solved[3] == 0 && time >= 2 && time <= 6) {
                            if(!(done[2] == 0 && solved[3] == 0 && time >= 2 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[3] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[2] == 0 && solved[6] == 0 && time >= 3 && time <= 6) {
                            if(!(done[2] == 0 && solved[6] == 0 && time >= 3 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[6] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (done[2] == 0 && solved[10] == 0 && time >= 6 && time <= 6) {
                            if(!(done[2] == 0 && solved[10] == 0 && time >= 6 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[10] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Ceska() {
                return false;
            }

            private boolean exec_Svobodak() {
                switch(java_randomGenerator.nextInt(6)) {
                    case 0:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 4:
                        if (body >= 10 && done[2] == 0) {
                            if(!(body >= 10 && done[2] == 0)) return false;
                            done[2] = (byte) (1);
                            solved[17] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 5:
                        if (done[2] == 0 && solved[5] == 0 && time >= 5 && time <= 5) {
                            if(!(done[2] == 0 && solved[5] == 0 && time >= 5 && time <= 5)) return false;
                            done[2] = (byte) (1);
                            solved[5] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        } else if(done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Petrov() {
                switch(java_randomGenerator.nextInt(4)) {
                    case 0:
                        if (body >= 10 && done[2] == 0) {
                            if(!(body >= 10 && done[2] == 0)) return false;
                            done[2] = (byte) (1);
                            solved[16] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                    case 3:
                        if (done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[2] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Petrov;
                            return true;
                        } else if(done[2] == 0 && solved[4] == 0 && time >= 5 && time <= 5) {
                            if(!(done[2] == 0 && solved[4] == 0 && time >= 5 && time <= 5)) return false;
                            done[2] = (byte) (1);
                            solved[4] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Petrov;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Spilberk() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Petrov;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Studovna;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0 && solved[1] == 0 && time >= 0 && time <= 4) {
                            if(!(done[2] == 0 && solved[1] == 0 && time >= 0 && time <= 4)) return false;
                            done[2] = (byte) (1);
                            solved[1] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Spilberk;
                            return true;
                        } else if(done[2] == 0 && solved[8] == 0 && time >= 8 && time <= 9) {
                            if(!(done[2] == 0 && solved[8] == 0 && time >= 8 && time <= 9)) return false;
                            done[2] = (byte) (1);
                            solved[8] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Spilberk;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Malinak() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6) {
                            if(!(done[2] == 0 && solved[7] == 0 && time >= 6 && time <= 6)) return false;
                            done[2] = (byte) (1);
                            solved[7] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Malinak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Svobodak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Jaroska() {
                switch(java_randomGenerator.nextInt(3)) {
                    case 0:
                        if (done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2) {
                            if(!(done[2] == 0 && solved[0] == 0 && time >= 0 && time <= 2)) return false;
                            done[2] = (byte) (1);
                            solved[0] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 1:
                        if (solved[18] == 1 && done[2] == 0) {
                            if(!(solved[18] == 1 && done[2] == 0)) return false;
                            done[2] = (byte) (1);
                            solved[19] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Jaroska;
                            return true;
                        }
                        return false;
                    case 2:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Tyrs() {
                switch(java_randomGenerator.nextInt(2)) {
                    case 0:
                        if (done[2] == 0) {
                            if(!(done[2] == 0)) return false;
                            done[2] = (byte) (1);

                            java_currentState = Java_Person_2Thread.States.Moravak;
                            return true;
                        }
                        return false;
                    case 1:
                        if (done[2] == 0 && solved[2] == 0 && time >= 1 && time <= 4) {
                            if(!(done[2] == 0 && solved[2] == 0 && time >= 1 && time <= 4)) return false;
                            done[2] = (byte) (1);
                            solved[2] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Tyrs;
                            return true;
                        } else if(done[2] == 0 && solved[14] == 0 && time >= 9 && time <= 13) {
                            if(!(done[2] == 0 && solved[14] == 0 && time >= 9 && time <= 13)) return false;
                            done[2] = (byte) (1);
                            solved[14] = (byte) (1);
                            body = (byte) (body + 1);

                            java_currentState = Java_Person_2Thread.States.Tyrs;
                            return true;
                        }
                        return false;
                }
                return false;
            }

            private boolean exec_Burian() {
                if (done[2] == 0) {
                    if(!(done[2] == 0)) return false;
                    done[2] = (byte) (1);

                    java_currentState = Java_Person_2Thread.States.Wilson;
                    return true;
                }
                return false;
            }

            private boolean exec_Wilson() {
                if (done[2] == 0) {
                    if(!(done[2] == 0)) return false;
                    atmodul = (byte) (atmodul + 1);
                    done[2] = (byte) (1);

                    java_currentState = Java_Person_2Thread.States.Modul;
                    return true;
                }
                return false;
            }

            private boolean exec_Modul() {
                return false;
            }

            // Execute method
            private void exec() {
                boolean result = false;
                while(java_transition_counter < java_COUNTER_BOUND) {
                    switch(java_currentState) {
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
                    java_t = new Thread(this, "Person_2Thread");
                    java_t.start();
                }
            }
        }

        // Constructor for main class
        GlobalClass(byte atmodul, byte body, byte[] done, byte[] solved, byte time) {
            // Instantiate global variables
            this.time = time;
            this.done = done;
            this.atmodul = atmodul;
            this.body = body;
            this.solved = solved;
            java_T_Timer = new GlobalClass.Java_TimerThread();
            java_T_Person_0 = new GlobalClass.Java_Person_0Thread();
            java_T_Person_1 = new GlobalClass.Java_Person_1Thread();
            java_T_Person_2 = new GlobalClass.Java_Person_2Thread();
        }

        // Start all threads
        public void startThreads() {
            java_T_Timer.start();
            java_T_Person_0.start();
            java_T_Person_1.start();
            java_T_Person_2.start();
        }

        // Join all threads
        public void joinThreads() {
            while (true) {
                try {
                    java_T_Timer.join();
                    java_T_Person_0.join();
                    java_T_Person_1.join();
                    java_T_Person_2.join();
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
        dve_exit_5 java_ap = new dve_exit_5();
        java_ap.startThreads();
        java_ap.joinThreads();
    }
}
