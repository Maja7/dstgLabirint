
import networkx as nx  
import numpy as np
import queue
import random

#postavke (minimalno 3 x 3)
brojRedaka=5
brojStupaca=5
#*******

class Celija:
  def __init__(self, x, y, posjeceno):
    self.koordinate=(x,y)
    self.posjeceno = posjeceno
    self.susjedi=[]
    self.s=[]
    self.children=[]
    self.razina=0

class cell:
  def __init__(self,koordinate,broj):
    self.koordinate=koordinate
    self.broj=broj
  
def generirajCelije(x,y,lista):
  for i in range (0,x):
    for j in range (0,y):
      lista.append(Celija(i,j,False))

def popuniSusjede1(lista):
  for c in range(0,brojRedaka*brojStupaca):
    if(c==0):
      lista[c].susjedi.append(1)
      lista[c].susjedi.append(brojStupaca)
    elif(c==brojStupaca-1):
      lista[c].susjedi.append(c-1)
      lista[c].susjedi.append(c+brojStupaca)
    elif(c==brojStupaca*(brojRedaka-1)):
      lista[c].susjedi.append(c-brojStupaca)
      lista[c].susjedi.append(c+1)
    elif(c==brojRedaka*brojStupaca-1):
      lista[c].susjedi.append(c-brojStupaca)
      lista[c].susjedi.append(c-1)
    elif(c in range (1,brojStupaca-1)):
      lista[c].susjedi.append(c+1)
      lista[c].susjedi.append(c-1)
      lista[c].susjedi.append(c+brojStupaca)
    elif(c%brojStupaca==0 and c!=0 and c!=brojStupaca*(brojRedaka-1)):
      lista[c].susjedi.append(c+1)
      lista[c].susjedi.append(c+brojStupaca)
      lista[c].susjedi.append(c-brojStupaca)
    elif(c%brojStupaca==brojStupaca-1 and c!=brojStupaca-1 and c!=brojRedaka*brojStupaca-1):
      lista[c].susjedi.append(c-1)
      lista[c].susjedi.append(c-brojStupaca)
      lista[c].susjedi.append(c+brojStupaca)
    elif(c in range (brojStupaca*(brojRedaka-1)+1,brojRedaka*brojStupaca-1)):
      lista[c].susjedi.append(c-1)
      lista[c].susjedi.append(c+1)
      lista[c].susjedi.append(c-brojStupaca)
    else:
      lista[c].susjedi.append(c+1)
      lista[c].susjedi.append(c-1)
      lista[c].susjedi.append(c+brojStupaca)
      lista[c].susjedi.append(c-brojStupaca)

def randomN(redak,stupac):
  svi=[]
  x = (stupac-1)*[0] + list(range(redak)) + (stupac-1)*[redak-1] + list(range(redak-1))[:0:-1]
  y = list(range(stupac)) + (redak-1)*[stupac-1] + list(range(stupac-1))[:0:-1] + (redak-1)*[0]
  for i,j in zip(x,y):
      svi.append(i*stupac + j)
  return random.choice(svi)
##########################
           
red=queue.Queue()
listaCelija1=[];

generirajCelije(brojRedaka,brojStupaca,listaCelija1)
popuniSusjede1(listaCelija1)

#+++++++++++++++++++++++++++++++++++++++++++++++#
#1
n = randomN(brojRedaka,brojStupaca)
listaCelija1[n].razina=0
korijen=listaCelija1[n].koordinate

while(1):
  #3
  listaCelija1[n].posjeceno=True

  #2
  c=cell(listaCelija1[n].koordinate,n)
  red.put(c)
  #4
  neposjeceniSusjediCelije=[]
  for el in listaCelija1[n].susjedi:
    if(listaCelija1[el].posjeceno==False):
      neposjeceniSusjediCelije.append(el)
  if(len(neposjeceniSusjediCelije)==0):
    while(red.empty()==False):
      celija=red.get()
      n=celija.broj
      for elem in listaCelija1[n].susjedi:
        if(listaCelija1[elem].posjeceno==False):
          neposjeceniSusjediCelije.append(elem)
      if(len(neposjeceniSusjediCelije)!=0):
        break
  
  if(len(neposjeceniSusjediCelije)==0):
    break
  a=random.choice(neposjeceniSusjediCelije)

  #5
  listaCelija1[a].s.append(listaCelija1[n].koordinate)
  listaCelija1[n].s.append(listaCelija1[a].koordinate)
    
  listaCelija1[n].children.append(listaCelija1[a].koordinate)
  listaCelija1[a].razina=listaCelija1[n].razina+1

  #6
  n=a

  #7 petlja
#+++++++++++++++++++++++++++++++++++++++++++++++#

def vratiKrajeve(lista):
    krajevi=[]
    maxRazina=0
    for celija in lista:
        if celija.razina>maxRazina:
            maxRazina=celija.razina

    for celija in lista:
        if(celija.razina==maxRazina):
            krajevi.append(celija.koordinate)
    return krajevi

krajevi=vratiKrajeve(listaCelija1)


print(korijen)
print(krajevi)

nikola = {}
for item in listaCelija1:
  nikola[item.koordinate] = item.s
  print(str(item.koordinate) + "*" + str(item.s))
print(nikola)

#crtanje grafa#

graf=[]
for c in listaCelija1:
    for d in c.children:
        graf.append((c.koordinate,d))



def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
    '''
    see hierarchy_pos docstring for most arguments

    pos: a dict saying where all nodes go if they have been assigned
    parent: parent of this branch. - only affects it if non-directed

    '''

    if pos is None:
        pos = {root:(xcenter,vert_loc)}
    else:
        pos[root] = (xcenter, vert_loc)
    children = list(G.neighbors(root))
    if not isinstance(G, nx.DiGraph) and parent is not None:
        children.remove(parent)  
    if len(children)!=0:
        dx = width/len(children) 
        nextx = xcenter - width/2 - dx/2
        for child in children:
            nextx += dx
            pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                vert_loc = vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                parent = root)
    return pos

def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''

    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch 
    - if the tree is directed and this is not given, the root will be found and used
    - if the tree is directed and this is given, then the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = random.choice(list(G.nodes))

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)

G=nx.Graph()

G.add_edges_from(graf)
pos=hierarchy_pos(G,korijen)
nx.draw(G, pos=pos, with_labels=True, node_size=2000)

