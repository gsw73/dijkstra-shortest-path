import sys
import time
import functools
import math

def clock( func ):
    @functools.wraps( func )
    def wrapper( *args, **kwargs ):
        t0 = time.perf_counter()
        result = func( *args, **kwargs )
        t1 = time.perf_counter()

        elapsedTime = t1 - t0
        if elapsedTime < 1e-3:
            units = 'us'
            scale = 1e-6
        elif elapsedTime < 1:
            units = 'ms'
            scale = 1e-3
        else:
            units = 's'
            scale = 1

        print( '[{1:8.2f}{2:s}] {0:s}'.format( func.__name__, (t1 - t0)/scale, units ) ) 
        return result
    return wrapper

@clock
def readFromFile( n, inputFile ):
    vArr = [ None for i in range( n + 1 ) ]

    # read file into vertex object array structure
    with open( inputFile, 'rt' ) as fin:
        while True:
            line = fin.readline()
            if not line:
                break

            # break line into components
            wholeLine = line.split()

            # first number is vertex
            v = int( wholeLine.pop( 0 ) )

            # create object
            vertex = Vertex( v )

            # remaining numbers are edges with weights
            for ew in wholeLine:
                edge, weight = ( int( i ) for i in ew.split( ',' ) )
                vertex.add_edge( edge, weight )

            # add to array
            vArr[ v ] = vertex

        return( vArr )

class Heap:

    def __init__( self, vlist = None ):
        if vlist == None:
            self.heap = []
        else:
            self.heap = list( vlist )

        self.n = len( vlist )

    def parent( self, loc ):
        return math.floor( ( loc - 1 ) / 2 )

    def l_child( self, loc ):
        return 2 * loc + 1

    def r_child( self, loc ):
        return 2 * loc + 2

    def swap( self, loc_a, loc_b ):
        # do the swap
        self.heap[ loc_a ], self.heap[ loc_b ] = self.heap[ loc_b ], self.heap[ loc_a ]

        # update node locations
        self.heap[ loc_a ].set_location( loc_a )
        self.heap[ loc_b ].set_location( loc_b )

        return

    def smallest_child_loc( self, location ):
        left_child_loc = self.l_child( location )
        right_child_loc = self.r_child( location )

        if self.heap[ left_child_loc ].key() <= self.heap[ right_child_loc ].key():
            return left_child_loc

        else:
            return right_child_loc

    def bubble_up( self, location ):
        if location == 0 or self.heap[ self.parent( location ) ].key() <= self.heap[ location ].key():
            return

        self.swap( self.parent( location ), location ) 

        self.bubble_up( self.parent( location ) )

        return

    def one_child( self, location ):
        last_index = len( self.heap ) - 1
        if self.l_child( location ) == last_index:
            return True

        else:
            return False

    def no_children( self, location ):
        last_index = len( self.heap ) - 1
        if self.l_child( location ) > last_index:
            return True

        else:
            return False

    def bubble_down( self, location ):
        # no children... done
        if self.no_children( location ):
            return

        # only one child to compare to
        if self.one_child( location ) and self.heap[ location ].key() <= self.heap[ self.l_child( location ) ].key():
            return

        # two children
        if self.heap[ location ].key() <= self.heap[ self.l_child( location ) ].key() and self.heap[ location ].key() <= self.heap[ self.r_child( location ) ].key():
            return

        # otherwise, need to swap
        if self.one_child( location ):
            swap_child_loc = self.l_child( location )

        else:
            swap_child_loc = self.smallest_child_loc( location )

        self.swap( swap_child_loc, location )

        self.bubble_down( swap_child_loc )

        return

    def insert( self, vObj ):
        # place element at end of list
        self.heap.append( vObj )
        location = len( self.heap ) - 1

        # set location in element
        vObj.heapLocation = location

        # always bubble up on insert
        self.bubble_up( location )

        return

    def delete( self, location ):

        # need to return object being deleted
        removed_obj = self.heap[ location ]

        # get last object in heap; remove it
        last_obj = self.heap.pop()

        # if we remove the last object, no need to do anything else
        if removed_obj is last_obj:
            return removed_obj

        # if now empty, then nothing left to do;
        if len( self.heap ) == 0:
            return removed_obj

        # move last object into deleted spot
        self.heap[ location ] = last_obj
        self.heap[ location ].set_location( location )

        self.bubble_up( location )
        self.bubble_down( location )

        return removed_obj

    def __str__( self ):
        myst = ''
        for i in range( len( self.heap ) ):
            myst += '[{:4}]  vertex = {}, greedy = {}'.format( i, self.heap[i].v, self.heap[i].greedyScore )
            myst += '\n'

        return myst

class Vertex:
    SMAX = 1000000

    def __init__( self, vertexNum ):
        self.edges = []
        self.path = []
        self.greedyScore = Vertex.SMAX
        self.heapLocation = vertexNum - 1
        self.v = vertexNum

    def set_location( self, l ):
        self.heapLocation = l
        return

    def key( self ):
        return( self.greedyScore )

    def add_edge( self, edge, weight ):
        self.edges.append( ( edge, weight ) )

    def __str__( self ):
        tString = ''
        for t in self.edges:
            tString = tString + str( t ) + ' '

        s = '{}:  greedyScore = {} heapLocation = {} (edge, weights): of {}; path = {}'.format(
                self.v,
                self.greedyScore,
                self.heapLocation,
                tString,
                self.path )
        return( s )

@clock
def dijkstra( verticies, my_heap, source ):
    MIN_LOC = 0
    set_x = set()

    # assumes source node at top of heap
    verticies[ source ].greedyScore = 0
    verticies[ source ].path.append( source )

    for i in range( len( my_heap.heap ) ):
        # delete min
        v_min = my_heap.delete( MIN_LOC )
        v_min.heapLocation = None
        set_x.add( v_min.v )

        # print( 'In round i = {}; v = {}'.format( i, v_min.v ) )
        # print( 'set_x = {}'.format( set_x ) )

        for edge, weight in v_min.edges:
            if verticies[ edge ].heapLocation == None:
                continue

            # these edge heads are in set(V-X) i.e., the heap
            new_path_weight = v_min.greedyScore + weight
            if new_path_weight < verticies[ edge ].greedyScore:
                v_to_update = my_heap.delete( verticies[ edge ].heapLocation )
                v_to_update.greedyScore = new_path_weight
                v_to_update.path = list( v_min.path ) + [ v_to_update.v ]
                my_heap.insert( v_to_update )

def usage():
    print( 'my_prompt>  python3 shortest_path.y <nodes> <filename>' )

def main():
    vertexObjArr = []
    finalV = [ 7, 37, 59, 82, 99, 115, 133, 165, 188, 197 ]

    if len( sys.argv ) < 3:
        usage()
        return

    # n indicates number of nodes in graph
    n = int( sys.argv[ 1 ] )
    inputFileName = sys.argv[ 2 ]

    # read in edge/weights file
    vertexObjArr = readFromFile( n, inputFileName )

    # create heap starting at 1 because this is 1-based and heap is 0-based
    h = Heap( vertexObjArr[ 1: ] )

    source = 1
    dijkstra( vertexObjArr, h, source )

    for i in vertexObjArr:
        print( i )
        
    # below used for extracting specific programming exercise answer
#     for i in finalV:
#         print( vertexObjArr[ i ] )
# 
#     for i in finalV:
#         print( '[{:4}]:  shortest distance = {}'.format( i, vertexObjArr[ i ].greedyScore ) )
# 
#     ans = []
#     ans_st = ''
#     for i in finalV:
#         ans.append( vertexObjArr[ i ].greedyScore )
#         ans_st += '{},'.format( vertexObjArr[ i ].greedyScore )
# 
#     print( ans )
#     print( ans_st )


if __name__ == '__main__':
    main()
