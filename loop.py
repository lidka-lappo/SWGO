from single_file import single_file

def loop_over(files):
    for file_path in files:
        print(f"Processing file: {file_path}")
        ev1 = single_file(file_path, rpc=1)
        ev2 =  single_file(file_path, rpc=2)
      #  if max(ev1, ev2) > 0:
       #     ratio = (min(ev1, ev2) / max(ev1, ev2)) * 100
       # else:
       #     ratio = 0.0
        ratio = ev2/ev1 * 100
        print(f"ratio: {ratio:.2f}%")
        #print(f"Events in RPC1: {ev1}, Events in RPC2: {ev2}")


files = [

    "sest25269075114.mat",
    "sest25269075833.mat",
    "sest25269080550.mat",
    "sest25269081308.mat",

    # "sest25269081950.mat",
    # "sest25269082339.mat",
    # "sest25269082728.mat",
    # "sest25269083118.mat",
    # "sest25269083507.mat",
    # "sest25269083856.mat",
    # "sest25269084244.mat",
    # "sest25269084632.mat",
    # "sest25269085021.mat",
    # "sest25269085409.mat",
    # "sest25269085758.mat",
    # "sest25269090148.mat",
    # "sest25269090537.mat",
    # "sest25269090927.mat",
    # "sest25269091316.mat",
    # "sest25269091707.mat",
    # "sest25269092057.mat",
    # "sest25269092446.mat",
    # "sest25269092836.mat"

]

loop_over(files)
