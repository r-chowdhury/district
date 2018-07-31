def find(do_redistrict_filename):
    f = open(do_redistrict_filename)
    num_districts, num_blocks = [int(x) for x in f.readline().split()]
    for _ in range(num_districts):
        center_location_data = f.readline()
    populations = num_districts * [0]
    for line in f:
        s = line.split()
        for i in range(3,len(s),2):
            populations[int(s[i])] += int(s[i+1])
    min_district_population = min(populations)
    return [x - min_district_population for x in populations]


    
