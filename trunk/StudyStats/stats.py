import os, csv, math

def to_int(v):
 try:
   return int(v)
 except:
   return 0

def to_float(v):
    try:
        return float(v)
    except:
        return float(0)
    
def to_log(v):
    return math.log(to_float(v) + 1 or 1,math.e)
    
    
def normalize(value, max):
    numerator = to_log(value)
    denominator = to_log(max)
    return numerator/denominator
    
def group_stats(groups):
 stats = []
 stats.append(['type', '# events', 'average res', 'average exp', 'average rel res', 'average rel exp', 'max res', 'max exp', 'max rel res', 'max rel exp'])
 for name, dicts in groups.items():
   total_res = total_exp = total_rel_res = total_rel_exp = max_res = max_exp = max_rel_res = max_rel_exp = 0
   
   for d in dicts:
     total_res += to_int(d['# res'])
     total_exp += to_int(d['# exp'])
     total_rel_res += to_int(d['# rel res'])
     total_rel_exp += to_int(d['# rel exp'])
     max_res = max(max_res,to_int(d['# res']))
     max_exp = max(max_exp,to_int(d['# exp']))
     max_rel_res = max(max_rel_res,to_int(d['# rel res']))
     max_rel_exp = max(max_rel_exp,to_int(d['# rel exp']))

   ave_res = total_res/float(len(dicts))
   ave_exp = total_exp/float(len(dicts))
   ave_rel_res = total_rel_res/float(len(dicts))
   ave_rel_exp = total_rel_exp/float(len(dicts))
   
   stats.append([name, len(dicts), ave_res, ave_exp, ave_rel_res, ave_rel_exp, max_res, max_exp, max_rel_res, max_rel_exp])

 return stats
 
def order_by_numberexplored_totaltime(data):
    output = []
    output.append(["session","id","# rel res", "# rel exp","# exp not rel", "total time"])
    data.sort(lambda a,b: cmp(b["total time"], a["total time"]))
    data.sort(lambda a,b: cmp(b["# rel exp"], a["# rel exp"]))
    data.sort(lambda a,b: cmp(b["# exp"], a["# exp"]))
    for d in data:
        output.append([d["session"],d["id"],0-to_int(d["# rel res"]),to_int(d["# rel exp"]),to_int(d["# exp"])-to_int(d["# rel exp"]),"00:"+d["total time"]])
        
    return output    

def order_by_numberexplored_res(data):
    output = []
    output.append(["session","id","# rel res", "# rel exp","# exp not rel", "total time"])
    data.sort(lambda a,b: cmp(b["# res"], a["# res"]))
    data.sort(lambda a,b: cmp(b["# exp"], a["# exp"]))
    for d in data:
        output.append([d["session"],d["id"],0-to_int(d["# rel res"]),to_int(d["# rel exp"]),to_int(d["# exp"])-to_int(d["# rel exp"]),"00:"+d["total time"]])
        
    return output    

def order_by_numberresults_totaltime(data):
    output = []
    output.append(["session","id","# exp", "# res not exp", "total time"])
    data.sort(lambda a,b: cmp(b["total time"], a["total time"]))
    data.sort(lambda a,b: cmp(to_int(b["# exp"]), to_int(a["# exp"])))
    data.sort(lambda a,b: cmp(to_int(b["# res"]), to_int(a["# res"])))
    for d in data:
        output.append([d["session"],d["id"],to_int(d["# exp"]),to_int(d["# res"]),"00:"+d["total time"]])
        
    return output  

def order_by_episode_session(data):
    output = []
    output.append(["session","id","# res", "# rel res", "# rel exp","# exp not rel", "total time"])
    data.sort(lambda a,b: cmp(to_int(a["session"]), to_int(b["session"])))
    data.sort(lambda a,b: cmp(to_int(a["id"]), to_int(b["id"])))
    for d in data:
        output.append([d["session"],d["id"], to_int(d["# res"]),0-to_int(d["# rel res"]),to_int(d["# rel exp"]),to_int(d["# exp"])-to_int(d["# rel exp"]),"00:"+d["total time"]])
        
    return output    

def order_by_percentage_exp_res(data):
    output = []
    output.append(["session","id","% results exp", "% results rel", "% rel results exp", "total time"])
    data.sort(lambda a,b: cmp(to_int(a["session"]), to_int(b["session"])))
    data.sort(lambda a,b: cmp(to_int(a["id"]), to_int(b["id"])))
    temp = []
    for d in data:
        if to_float(d["# res"]) != to_float(0):
            p_exp = (to_float(d["# exp"])/to_float(d["# res"])) * 100
            p_rel = (to_float(d["# rel res"])/to_float(d["# res"])) * 100
            p_rel_exp = (to_float(d["# rel exp"])/to_float(d["# res"])) * 100
            temp.append([d["session"],d["id"],p_exp,p_rel, p_rel_exp,"00:"+d["total time"]])
    temp.sort(lambda a,b: cmp(to_int(b[2]), to_int(a[2])))
    output.extend(temp)

    return output

def order_by_normalized_exp(data):
    output = []
    output.append(["session","id","normalized results","normalized results exp", "normalized results rel", "normalized rel results exp", "total time"])
    data.sort(lambda a,b: cmp(to_int(a["session"]), to_int(b["session"])))
    data.sort(lambda a,b: cmp(to_int(a["id"]), to_int(b["id"])))
    temp = []
    max_res = 0;
    for d in data:
        max_res = max(max_res,to_int(d["# res"]))
    for d in data:
        if to_log(d["# res"]) != to_float(0):
            n_res = normalize(d["# res"],max_res)*100
            n_exp = normalize(d["# exp"],max_res)*100
            n_rel = normalize(d["# rel res"],max_res)*100
            n_rel_exp = normalize(d["# rel exp"],max_res)*100
            temp.append([d["session"],d["id"],n_res,n_exp,n_rel, n_rel_exp,"00:"+d["total time"]])
    temp.sort(lambda a,b: cmp(to_int(b[2]), to_int(a[2])))
    output.extend(temp)

    return output

def group_by_type(data):
 result = {}
 for d in data:
   t = d["search type"].lower().strip()
   result.setdefault(t, [])
   result[t].append(d)
 return result

def remove_cancelled(data):
    result = []
    for d in data:
        if 'cancelled' in d["# res"]:
            print 'removed'
        elif 'Invalid' in d["comments"]:
            print 'removed'
        elif 'Incomplete' in d["comments"]:
            print 'removed'    
        else:
            result.append(d)
    return result    

def remove_no_res(data):
    result = []
    for d in data:
        if not to_float(d["# res"]) is 0.0:
            result.append(d)
    return result            

def remove_non_relevant(data):
    result = []
    for d in data:
        if to_int(d["# rel res"]) > 0:
            result.append(d)
    return result        

def to_dict(header, row):
 return dict(zip(header,row))

def get_data():
 reader = csv.reader(open('combined/outputfile.csv'))
 head = [h.lower().strip() for h in reader.next()]
 return [to_dict(head,r) for r in reader]

stats = group_stats(group_by_type(get_data()))
w = csv.writer(open('combined/stats_by_type.csv', 'w'))
for s in stats:
 w.writerow(s)
 
stats = group_stats(group_by_type(remove_cancelled(get_data())))
w = csv.writer(open('combined/stats_by_type_not_cancelled.csv', 'w'))
for s in stats:
    w.writerow(s)                    
 
stats = group_stats(group_by_type(remove_non_relevant(get_data())))
w = csv.writer(open('combined/stats_by_type_when_relevant_exists.csv','w'))
for s in stats:
    w.writerow(s)
    
stats = order_by_numberexplored_totaltime(remove_cancelled(get_data()))
w = csv.writer(open('combined/data_sorted_by_exp_time.csv','w'))
for s in stats:
    w.writerow(s)

stats = order_by_numberexplored_res(remove_cancelled(get_data()))
w = csv.writer(open('combined/data_sorted_by_exp_res.csv','w'))
for s in stats:
    w.writerow(s)
    
stats = order_by_numberresults_totaltime(remove_cancelled(get_data()))    
w = csv.writer(open('combined/data_sorted_by_res.csv','w'))
for s in stats:
    w.writerow(s)
                 
stats = order_by_episode_session(remove_cancelled(get_data()))
w = csv.writer(open('combined/data_sorted_by_id_session.csv','w'))
for s in stats:
    w.writerow(s)          
    
stats = order_by_percentage_exp_res(remove_cancelled(get_data()))
w = csv.writer(open('combined/data_sorted_by_percentage.csv','w'))
for s in stats:
    w.writerow(s)                     
                      
stats = order_by_normalized_exp(remove_cancelled(get_data()))
w = csv.writer(open('combined/data_sorted_normalized.csv','w'))
for s in stats:
    w.writerow(s)                                                               