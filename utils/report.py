from tabulate import tabulate

def print_report(rows, headers):
    if not rows or len(rows)==0:
        print("No data given.\n")
        return
    
    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
    print("")