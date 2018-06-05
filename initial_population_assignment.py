def gen(assignment_filename):
    f = open(assignment_filename)
    k, n = [int(x) for x in f.readline().split()]
    for _ in range(k): foo = f.readline()
    for line in f:
        items = line.split()
        ID = int(items[0])
        assignment_data = [int(x) for x in items[3:]]
        districts = [assignment_data[i] for i in range(0, len(assignment_data), 2)]
        subpops = [assignment_data[i] for i in range(1, len(assignment_data), 2)]
        pop_assignment = {district:subpop for district,subpop in zip(districts, subpops)}
        yield ID, pop_assignment

'''
for x in gen("data/RI_new_assignment.txt"):
  print(x)
'''
