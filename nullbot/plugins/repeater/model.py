from collections import defaultdict, OrderedDict

class LFUNode:
  def __init__(self, key, object, count):
    self.key = key
    self.object = object
    self.count = count

class LFUCache:
  """Least frequently used cache for repeating bullshit"""
  def __init__(self, capacity: int, callback = None):
    self.capacity = capacity
    self.key_to_node = {}
    self.count_to_ordered_node = defaultdict(OrderedDict)
    self.min_count = -1
    self.callback = callback

  async def get(self, key):
    if key not in self.key_to_node:
      return None
    
    node = self.key_to_node[key]
    del self.count_to_ordered_node[node.count][key]
    if not self.count_to_ordered_node[node.count]:
      del self.count_to_ordered_node[node.count]
      if self.min_count == node.count:
        self.min_count += 1

    node.count += 1
    self.count_to_ordered_node[node.count][key] = node

    # check callback trigger
    await self.callback(node)

    return node.object

  async def put(self, key, object = None):
    if key in self.key_to_node:
      self.key_to_node[key].object = object
      await self.get(key)
      return
    
    if len(self.key_to_node) == self.capacity:
      k, _ = self.count_to_ordered_node[self.min_count].popitem(last=False) # FIFO
      del self.key_to_node[k]
    
    self.key_to_node[key] = LFUNode(key, object, 1)
    self.count_to_ordered_node[1][key] = self.key_to_node[key]
    self.min_count = 1

    return
