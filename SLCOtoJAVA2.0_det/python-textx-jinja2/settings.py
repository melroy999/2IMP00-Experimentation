add_counter = False
add_performance_counter = False
print_decision_report = False


def init(add_counter_var, add_performance_counters_var, print_decision_report_var):
    global add_counter, add_performance_counter, print_decision_report
    add_counter = add_counter_var
    add_performance_counter = add_performance_counters_var
    print_decision_report = print_decision_report_var
