class Queue:

  def __init__(self):
      self.queue = list()

  def enqueue(self,data):
      if data not in self.queue:
          self.queue.insert(0,data)
          return True
      return False

  def dequeue(self):
      if len(self.queue)>0:
          return self.queue.pop()
      return ("Prazan red!")

  def size(self):
      return len(self.queue)

  def printQueue(self):
      return self.queue

red=Queue()


