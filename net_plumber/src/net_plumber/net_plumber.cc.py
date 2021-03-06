'''
   Copyright 2012 Google Inc.

   Licensed under the Apache License, 2.0 (the "License")
   you may not use self file except in compliance with the License.
   You may obtain a copy of the License at

       http:#www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   Author: peyman.kazemian@gmail.com (Peyman Kazemian)
'''

#include "net_plumber.h"
#include <stdio.h>
#include <assert.h>
#include <stdlib.h>
#include <sstream>
#include <fstream>
#include "net_plumber_utils.h"
#include "../jsoncpp/json/json.h"

using namespace std
using namespace log4cxx
using namespace net_plumber

LoggerPtr NetPlumber.logger(Logger.getLogger("NetPlumber"))
LoggerPtr loop_logger(Logger.getLogger("DefaultLoopDetectionLogger"))

def flow_to_str(self, *f):  stringstream str
  char buf[50]
  while(f.p_flow != f.node.get_EOSFI())    h = hs_to_str(f.hs_object)
    sprintf(buf,"0x%llx",f.node.node_id)
    str << h << " @ " << buf << " <-- "
    free(h)
    f = *f.p_flow

  h = hs_to_str(f.hs_object)
  str << h
  free(h)
  return str.str()


def default_loop_callback(self, *N, *f, *data):  e = N.get_last_event()
  stringstream error_msg
  error_msg << "Loop Detected: after event " << get_event_name(e.type) <<
      " (ID1: " << e.id1 << ")" << endl << flow_to_str(f)
  LOG4CXX_FATAL(loop_logger,error_msg.str())


def default_blackhole_callback(self, *N, *f, *data):  e = N.get_last_event()
  stringstream error_msg
  error_msg << "Black Hole Detected: after event " << get_event_name(e.type) <<
      " (ID1: " << e.id1 << ")"
  LOG4CXX_FATAL(loop_logger,error_msg.str())


def get_event_name(self, t):  switch (t)    case(1): return "Add Rule"
    case(2): return "Remove Rule"
    case(3): return "Add Link"
    case(4): return "Remove Link"
    case(5): return "Add Source"
    case(6): return "Remove Source"
    case(7): return "Add Sink"
    case(8): return "Remove Sink"
    case(9): return "Start Source Probe"
    case(10): return "Stop Source Probe"
    case(11): return "Start Sink Probe"
    case(12): return "Stop Sink Probe"
    case(13): return "Add Table"
    case(14): return "Remove Table"
    default: return "None"



'''
 * * * * * * * * * * * * * *
 * Private Helper Members  *
 * * * * * * * * * * * * * *
 '''

def free_group_memory(self, table, group):  list<RuleNode*>rules_list = table_to_nodes[table]
  list<RuleNode*>.iterator it,tmp
  for ( it=rules_list.begin() ; it != rules_list.end(); )    if (*it).group == group:      free_rule_memory(*it,False)
      tmp = it; it++
      rules_list.erase(tmp)
    } else it++



def free_rule_memory(self, *r, remove_from_table):  if remove_from_table) table_to_nodes[r.table].remove(r:
  id_to_node.erase(r.node_id)
  clear_port_to_node_maps(r)
  delete r


def free_table_memory(self, table):  if table_to_nodes.count(table) > 0:    table_to_last_id.erase(table)
    list<RuleNode*>rules_list = table_to_nodes[table]
    list<RuleNode*>.iterator it
    for ( it=rules_list.begin() ; it != rules_list.end(); it++ )      free_rule_memory(*it,False)

    table_to_nodes.erase(table)
    delete rules_list
    free(table_to_ports[table].list)
    table_to_ports.erase(table)
  } else:
    stringstream error_msg
    error_msg << "Table " << table << " does not exist. Can't delete it."
    LOG4CXX_WARN(logger,error_msg.str())



def set_port_to_node_maps(self, *n):  for (i = 0; i < n.input_ports.size; i++)    if inport_to_nodes.count(n.input_ports.list[i]) == 0:      inport_to_nodes[n.input_ports.list[i]] = list<Node*>(1,n)
    } else:
      inport_to_nodes[n.input_ports.list[i]].push_back(n)


  for (i = 0; i < n.output_ports.size; i++)    if outport_to_nodes.count(n.output_ports.list[i]) == 0:      outport_to_nodes[n.output_ports.list[i]] = list<Node*>(1,n)
    } else:
      outport_to_nodes[n.output_ports.list[i]].push_back(n)




def clear_port_to_node_maps(self, *n):  for (i = 0; i < n.input_ports.size; i++)    inport_to_nodes[n.input_ports.list[i]].remove(n)
    if inport_to_nodes[n.input_ports.list[i]].size() == 0:      delete inport_to_nodes[n.input_ports.list[i]]
      inport_to_nodes.erase(n.input_ports.list[i])


  for (i = 0; i < n.output_ports.size; i++)    outport_to_nodes[n.output_ports.list[i]].remove(n)
    if outport_to_nodes[n.output_ports.list[i]].size() == 0:      delete outport_to_nodes[n.output_ports.list[i]]
      outport_to_nodes.erase(n.output_ports.list[i])




def set_table_dependency(self, *r):  if (r.group != 0 and r.group != r.node_id) return; #escape non-group-lead
  list<RuleNode*>rules_list = table_to_nodes[r.table]
  list<RuleNode*>.iterator it
  seen_rule = False
  for (it=rules_list.begin() ; it != rules_list.end(); it++)    if (*it).node_id == r.node_id:      seen_rule = True
    } elif (*it).group != 0 and (*it).node_id != (*it).group:      # escape *it, *it belongs to a group and is not the lead of the group.
      continue
    } else:
      # find common input ports
      common_ports = intersect_sorted_lists(r.input_ports,
                                                  (*it).input_ports)
      if (common_ports.size == 0) continue
      # find common headerspace
      array_t *common_hs = array_isect_a(r.match,(*it).match,self.length)
      if common_hs == NULL:        if not common_ports.shared) free(common_ports.list:
        continue

      # add influence
      Influence *inf = (Influence *)malloc(sizeof *inf)
      Effect *eff = (Effect *)malloc(sizeof *eff)
      inf.comm_arr = common_hs
      inf.ports = common_ports
      if seen_rule:        inf.node = (*it)
        eff.node = r
        eff.influence = (*it).set_influence_by(inf)
        inf.effect = r.set_effect_on(eff)
      } else:
        inf.node = r
        eff.node = (*it)
        eff.influence = r.set_influence_by(inf)
        inf.effect = (*it).set_effect_on(eff)





def set_node_pipelines(self, *n):  # set n's forward pipelines.
  for (i = 0; i < n.output_ports.size; i++)    vector<uint32_t> *end_ports = get_dst_ports(n.output_ports.list[i])
    if (not end_ports) continue
    for (j = 0; j < end_ports.size(); j++)      list<Node*> *potential_next_rules =
          get_nodes_with_inport(end_ports.at(j))
      if (not potential_next_rules) continue
      list<Node*>.iterator it
      for (it = potential_next_rules.begin()
           it != potential_next_rules.end(); it++)        array_t *pipe_arr = array_isect_a((*it).match, n.inv_match, length)
        if pipe_arr:          Pipeline *fp = (Pipeline *)malloc(sizeof *fp)
          Pipeline *bp = (Pipeline *)malloc(sizeof *bp)
          fp.local_port = n.output_ports.list[i]
          bp.local_port = end_ports.at(j)
          fp.pipe_array = pipe_arr
          bp.pipe_array = pipe_arr
          fp.node = n
          bp.node = *it
          bp.r_pipeline = n.add_fwd_pipeline(fp)
          fp.r_pipeline = (*it).add_bck_pipeline(bp)




  # set n's backward pipelines.
  for (i = 0; i < n.input_ports.size; i++)    vector<uint32_t> *orig_ports = get_src_ports(n.input_ports.list[i])
    if (not orig_ports) continue
    for (j = 0; j < orig_ports.size(); j++)      list<Node*> *potential_prev_rules =
          get_nodes_with_outport(orig_ports.at(j))
      if (not potential_prev_rules) continue
      list<Node*>.iterator it
      for (it = potential_prev_rules.begin()
           it != potential_prev_rules.end(); it++)        array_t *pipe_arr = array_isect_a((*it).inv_match, n.match, length)
        if pipe_arr:          Pipeline *fp = (Pipeline *)malloc(sizeof *fp)
          Pipeline *bp = (Pipeline *)malloc(sizeof *bp)
          fp.local_port = orig_ports.at(j)
          bp.local_port = n.input_ports.list[i]
          fp.pipe_array = pipe_arr
          bp.pipe_array = pipe_arr
          fp.node = *it
          bp.node = n
          bp.r_pipeline = (*it).add_fwd_pipeline(fp)
          fp.r_pipeline = n.add_bck_pipeline(bp)






'''
 * * * * * * * * * * * * *
 * Public Class Members  *
 * * * * * * * * * * * * *
 '''

NetPlumber.NetPlumber(int length) : length(length), last_ssp_id_used(0)  self.last_event.type = None
  self.loop_callback = default_loop_callback
  self.loop_callback_data = NULL
  self.blackhole_callback = default_loop_callback
  self.blackhole_callback_data = NULL


NetPlumber.~NetPlumber()  list<Node*>.iterator p_it
  for (p_it = probes.begin(); p_it != probes.end(); p_it++)    if (*p_it).get_type() == SOURCE_PROBE:      ((SourceProbeNode*)(*p_it)).stop_probe()

    clear_port_to_node_maps(*p_it)
    delete *p_it

  map< uint32_t, std.vector<uint32_t>* >.iterator it
  for (it = topology.begin(); it != topology.end(); it++ )    delete (*it).second

  for (it = inv_topology.begin(); it != inv_topology.end(); it++ )    delete (*it).second

  map< uint32_t,std.list<RuleNode*>* >.iterator it2,tmp2
  for (it2 = table_to_nodes.begin(); it2 != table_to_nodes.end(); )    tmp2 = it2
    tmp2++
    free_table_memory((*it2).first)
    it2 = tmp2

  list<Node*>.iterator s_it
  for (s_it = flow_nodes.begin(); s_it != flow_nodes.end(); s_it++)    clear_port_to_node_maps(*s_it)
    delete *s_it



def get_last_event(self):  return self.last_event


def set_last_event(self, e):  self.last_event = e


def add_link(self, from_port, to_port):  self.last_event.type = ADD_LINK
  self.last_event.id1 = from_port
  self.last_event.id2 = to_port
  # topology update
  if topology.count(from_port) == 0:    topology[from_port] = vector<uint32_t>(1,to_port)
  } else:
    topology[from_port].push_back(to_port)

  if inv_topology.count(to_port) == 0:    inv_topology[to_port] = vector<uint32_t>(1,from_port)
  } else:
    inv_topology[to_port].push_back(from_port)


  # pipeline update
  list<Node*> *src_rules = self.get_nodes_with_outport(from_port)
  list<Node*> *dst_rules = self.get_nodes_with_inport(to_port)
  list<Node*>.iterator src_it,dst_it
  if src_rules and dst_rules:    for (src_it = src_rules.begin(); src_it != src_rules.end(); src_it++)      for (dst_it = dst_rules.begin(); dst_it != dst_rules.end(); dst_it++)        array_t *pipe_arr = array_isect_a((*src_it).inv_match,
                                         (*dst_it).match,
                                         length)
        if pipe_arr:          Pipeline *fp = (Pipeline *)malloc(sizeof *fp)
          Pipeline *bp = (Pipeline *)malloc(sizeof *bp)
          fp.local_port = from_port
          bp.local_port = to_port
          fp.pipe_array = pipe_arr
          bp.pipe_array = pipe_arr
          fp.node = *src_it
          bp.node = *dst_it
          bp.r_pipeline = (*src_it).add_fwd_pipeline(fp)
          fp.r_pipeline = (*dst_it).add_bck_pipeline(bp)
          (*src_it).propagate_src_flows_on_pipe(bp.r_pipeline)






def remove_link(self, from_port, to_port):  self.last_event.type = REMOVE_LINK
  self.last_event.id1 = from_port
  self.last_event.id2 = to_port
  if topology.count(from_port) == 0 or inv_topology.count(to_port) == 0:    stringstream error_msg
    error_msg << "Link " << from_port << "-." << to_port <<
        " does not exist. Can't remove it."
    LOG4CXX_ERROR(logger,error_msg.str())
  } else:
    # remove plumbing
    list<Node*> *src_rules = self.get_nodes_with_outport(from_port)
    list<Node*> *dst_rules = self.get_nodes_with_inport(to_port)
    list<Node*>.iterator src_it
    if src_rules and dst_rules:      for (src_it = src_rules.begin(); src_it != src_rules.end(); src_it++)        (*src_it).remove_link_pipes(from_port,to_port)



    # update topology and inv_topology
    vector<uint32_t>.iterator it
    vector<uint32_t> *v = topology[from_port]
    vector<uint32_t> *v_inv = inv_topology[to_port]
    for (it = v.begin(); it != v.end(); it++)      if (*it) == to_port:        v.erase(it)
        break


    for (it = v_inv.begin(); it != v_inv.end(); it++)      if (*it) == to_port:        v.erase(it)
        break





vector<uint32_t> *NetPlumber.get_dst_ports(uint32_t src_port)  if topology.count(src_port) == 0:    return NULL
  } else:
    return topology[src_port]



vector<uint32_t> *NetPlumber.get_src_ports(uint32_t dst_port)  if inv_topology.count(dst_port) == 0:    return NULL
  } else:
    return inv_topology[dst_port]



def print_topology(self):  map< uint32_t, std.vector<uint32_t>* >.iterator it
  for (it = topology.begin(); it != topology.end(); it++ )    printf("%u -. ( ",(*it).first)
    for (i = 0; i < (*it).second.size(); i++)      printf("%u ",(*it).second.at(i))

    printf(")\n")



def add_table(self, id, ports):  self.last_event.type = ADD_TABLE
  self.last_event.id1 = id
  assert(table_to_nodes.count(id) == table_to_last_id.count(id))
  if table_to_nodes.count(id) == 0 and id > 0:    ports.shared = True

    table_to_nodes[id] = list<RuleNode*>()
    table_to_ports[id] = ports
    table_to_last_id[id] = 0
    return
  } elif id == 0:    LOG4CXX_ERROR(logger,"Can not create table with ID 0. ID should be > 0.")
  } else:
    stringstream error_msg
    error_msg << "Table " << id << " already exist. Can't add it again."
    LOG4CXX_ERROR(logger,error_msg.str())

  free(ports.list)


def remove_table(self, id):  self.last_event.type = REMOVE_TABLE
  self.last_event.id1 = id
  free_table_memory(id)


def get_table_ports(self, id):  return self.table_to_ports[id]


def print_table(self, id):  printf("%s\n",string(40,'@').c_str())
  printf("%sTable: 0x%x\n",string(4, ' ').c_str(),id)
  printf("%s\n",string(40,'@').c_str())
  list<RuleNode*>rules_list = table_to_nodes[id]
  list<RuleNode*>.iterator it
  ports = self.table_to_ports[id]
  printf("Ports: %s\n",list_to_string(ports).c_str())
  printf("Rules:\n")
  for ( it=rules_list.begin() ; it != rules_list.end(); it++ )    printf("%s\n",(*it).to_string().c_str())



uint64_t NetPlumber._add_rule(uint32_t table, index,
                               bool group, gid,
                               List_t in_ports, out_ports,
                               array_t* match, *mask, rw)  if table_to_nodes.count(table) > 0:    table_to_last_id[table] += 1
    id = table_to_last_id[table] + ((uint64_t)table << 32) 
    if (in_ports.size == 0) in_ports = table_to_ports[table]
    RuleNode *r
    if (not group or not gid) { #first rule in group or no group
      if (not group) r = RuleNode(self, length, id, table, in_ports, out_ports,
                                   match, mask, rw)
      r = RuleNode(self, length, id, table, id, in_ports, out_ports,
                            match, mask, rw)
      self.id_to_node[id] = r
      if index < 0 or index >= (int)self.table_to_nodes[table].size():        self.table_to_nodes[table].push_back(r)
      } else:
        list<RuleNode*>it = table_to_nodes[table].begin()
        for (int i=0; i < index; i++, it++)
        self.table_to_nodes[table].insert(it,r)

      self.last_event.type = ADD_RULE
      self.last_event.id1 = id
      self.set_port_to_node_maps(r)
      self.set_table_dependency(r)
      self.set_node_pipelines(r)
      r.subtract_infuences_from_flows()
      r.process_src_flow(NULL)

    } elif (id_to_node.count(gid) > 0 and
          ((RuleNode*)id_to_node[gid]).group == gid)
      RuleNode *rg = (RuleNode*)self.id_to_node[gid]
      table = rg.table
      r = RuleNode(self, length, id, table, gid, in_ports, out_ports,
                       match, mask, rw)
      self.id_to_node[id] = r
      # insert rule after its lead group rule
      list<RuleNode*>it = table_to_nodes[table].begin()
      for (; (*it).node_id != gid; it++)
      self.table_to_nodes[table].insert(++it,r)
      self.last_event.type = ADD_RULE
      self.last_event.id1 = id
      # set port maps
      self.set_port_to_node_maps(r)
      #The influences of self rule is the same as lead rule in the group.
      r.effect_on = rg.effect_on
      r.influenced_by = rg.influenced_by
      self.set_node_pipelines(r)
      # no need to subtract influences. it has already taken care of
      r.process_src_flow(NULL)

    } else:
      free(in_ports.list);free(out_ports.list);free(match);free(mask);free(rw)
      stringstream error_msg
      error_msg << "Group " << group << " does not exist. Can't add rule to it."
          << "Ignoring add rule request."
      LOG4CXX_WARN(logger,error_msg.str())
      return 0

    return id
  } else:
    free(in_ports.list);free(out_ports.list);free(match);free(mask);free(rw)
    stringstream error_msg
    error_msg << "trying to add a rule to a non-existing table (id: " << table
        << "). Ignored."
    LOG4CXX_ERROR(logger,error_msg.str())
    return 0



uint64_t NetPlumber.add_rule(uint32_t table, index, in_ports,
            List_t out_ports, match, *mask, rw)  return _add_rule(table,index,False,0,in_ports,out_ports,match,mask,rw)


uint64_t NetPlumber.add_rule_to_group(uint32_t table, index, in_ports
                           , out_ports, match, *mask,
                           array_t* rw, group)  return _add_rule(table,index,True,group,in_ports,out_ports,match,mask,rw)



def remove_rule(self, rule_id):  if id_to_node.count(rule_id) > 0 and id_to_node[rule_id].get_type() == RULE:    self.last_event.type = REMOVE_RULE
    self.last_event.id1 = rule_id
    RuleNode *r = (RuleNode *)id_to_node[rule_id]
    if r.group == 0) free_rule_memory(r:
    else free_group_memory(r.table,r.group)
  } else:
    stringstream error_msg
    error_msg << "Rule " << rule_id << " does not exist. Can't delete it."
    LOG4CXX_WARN(logger,error_msg.str())



def add_source(self, *hs_object, ports):  node_id = (uint64_t)(++last_ssp_id_used)
  SourceNode *s = SourceNode(self, length, node_id, hs_object, ports)
  self.id_to_node[node_id] = s
  self.flow_nodes.push_back(s)
  self.last_event.type = ADD_SOURCE
  self.last_event.id1 = node_id
  self.set_port_to_node_maps(s)
  self.set_node_pipelines(s)
  s.process_src_flow(NULL)
  return node_id


def remove_source(self, id):  if id_to_node.count(id) > 0 and id_to_node[id].get_type() == SOURCE:    self.last_event.type = REMOVE_SOURCE
    self.last_event.id1 = id
    SourceNode *s = (SourceNode *)id_to_node[id]
    id_to_node.erase(s.node_id)
    flow_nodes.remove(s)
    clear_port_to_node_maps(s)
    delete s
  } else:
    stringstream error_msg
    error_msg << "Source Node " << id << " does not exist. Can't delete it."
    LOG4CXX_WARN(logger,error_msg.str())



uint64_t NetPlumber.
add_source_probe(List_t ports, mode, *filter,
                 Condition *condition, probe_callback,
                 void *callback_data)  node_id = (uint64_t)(++last_ssp_id_used)
  p = SourceProbeNode(self, length, node_id, mode,ports,
                                           filter, condition,
                                           probe_callback, callback_data)
  self.id_to_node[node_id] = p
  self.probes.push_back(p)
  self.last_event.type = START_SOURCE_PROBE
  self.last_event.id1 = node_id
  self.set_port_to_node_maps(p)
  self.set_node_pipelines(p)
  p.process_src_flow(NULL)
  p.start_probe()
  return node_id


def remove_source_probe(self, id):  if id_to_node.count(id) > 0 and id_to_node[id].get_type() == SOURCE_PROBE:    self.last_event.type = STOP_SOURCE_PROBE
    self.last_event.id1 = id
    SourceProbeNode *p = (SourceProbeNode *)id_to_node[id]
    p.stop_probe()
    id_to_node.erase(p.node_id)
    probes.remove(p)
    clear_port_to_node_maps(p)
    delete p
  } else:
    stringstream error_msg
    error_msg << "Probe Node " << id << " does not exist. Can't delete it."
    LOG4CXX_WARN(logger,error_msg.str())



SourceProbeNode *NetPlumber.get_source_probe(uint64_t id)  if id_to_node.count(id) > 0:    Node *n = id_to_node[id]
    if n.get_type() == SOURCE_PROBE:      return (SourceProbeNode *)n


  return NULL


def get_nodes_with_outport(self, outport):  if outport_to_nodes.count(outport) == 0:    return NULL
  } else:
    return outport_to_nodes[outport]



def get_nodes_with_inport(self, inport):  if inport_to_nodes.count(inport) == 0:    return NULL
  } else:
    return inport_to_nodes[inport]



def print_plumbing_network(self):  map<uint32_t,std.list<RuleNode*>* >.iterator it
  for (it = table_to_nodes.begin(); it != table_to_nodes.end(); it++)    self.print_table((*it).first)

  printf("%s\n",string(40,'@').c_str())
  printf("%sSources and Sinks\n",string(4, ' ').c_str())
  printf("%s\n",string(40,'@').c_str())
  list<Node *>.iterator it2
  for (it2 = flow_nodes.begin(); it2 != flow_nodes.end(); it2++)    printf("%s\n",(*it2).to_string().c_str())

  printf("%s\n",string(40,'@').c_str())
  printf("%sProbes\n",string(4, ' ').c_str())
  printf("%s\n",string(40,'@').c_str())
  for (it2 = probes.begin(); it2 != probes.end(); it2++)    printf("%s\n",(*it2).to_string().c_str())



void NetPlumber.get_pipe_stats(uint64_t node_id, &fwd_pipeline,
                int &bck_pipeline, &influence_on, &influenced_by)  if id_to_node.count(node_id) == 0:    fwd_pipeline = 0
    bck_pipeline = 0
    influence_on = 0
    influenced_by = 0
    stringstream error_msg
    error_msg << "Requested pipe stats for a non-existing node " << node_id
        << "."
    LOG4CXX_ERROR(logger,error_msg.str())
  } else:
    Node *n = id_to_node[node_id]
    if n.get_type() == RULE:      RuleNode *r = (RuleNode *)n
      fwd_pipeline = r.count_fwd_pipeline()
      bck_pipeline = r.count_bck_pipeline()
      influence_on = r.count_effects()
      influenced_by = r.count_influences()
    } elif n.get_type() == SOURCE or n.get_type() == SINK:      fwd_pipeline = n.count_fwd_pipeline()
      bck_pipeline = n.count_bck_pipeline()
      influence_on = 0
      influenced_by = 0
    } elif n.get_type() == SOURCE_PROBE or n.get_type() == SINK_PROBE:      fwd_pipeline = n.count_fwd_pipeline()
      bck_pipeline = n.count_bck_pipeline()
      influence_on = 0
      influenced_by = 0
    } else:
      fwd_pipeline = 0
      bck_pipeline = 0
      influence_on = 0
      influenced_by = 0
      stringstream error_msg
      error_msg << "Node with type " << n.get_type() << " doesn't have stats."
      LOG4CXX_WARN(logger,error_msg.str())




def get_source_flow_stats(self, node_id, &inc, &exc):  if id_to_node.count(node_id) == 0:    inc = 0
    exc = 0
    stringstream error_msg
    error_msg << "Requested source flow stats for a non-existing node " <<
        node_id << "."
    LOG4CXX_ERROR(logger,error_msg.str())
  } else:
    Node *n = id_to_node[node_id]
    n.count_src_flow(inc,exc)



def save_dependency_graph(self, file_name):  map<uint64_t, it
  Json.Value root(Json.objectValue)
  Json.Value nodes(Json.arrayValue)
  Json.Value links(Json.arrayValue)
  map<uint64_t, ordering
  count = 0
  root["nodes"] = nodes
  root["links"] = links
  for (it = id_to_node.begin(); it != id_to_node.end(); it++)    stringstream s
    s << (*it).first
    Json.Value node(Json.objectValue)
    Json.Value name(Json.stringValue)
    name = s.str()
    node["name"] = name
    root["nodes"].append(node)
    ordering[(*it).first] = count
    count++

  for (it = id_to_node.begin(); it != id_to_node.end(); it++)    stringstream s1,s2
    s1 << (*it).first
    Node *n = (*it).second
    list<struct Pipeline*>.iterator pit
    for (pit = n.next_in_pipeline.begin(); pit != n.next_in_pipeline.end()
         pit++)      Node *other_n = (*(*pit).r_pipeline).node
      s2 << other_n.node_id
      Json.Value link(Json.objectValue)
      Json.Value source(Json.intValue)
      Json.Value target(Json.intValue)
      source = ordering[(*it).first]
      target = ordering[other_n.node_id]
      link["source"] = source
      link["target"] = target
      root["link"].append(link)



  ofstream jsfile(file_name.c_str())
  jsfile << root
  jsfile.close()

