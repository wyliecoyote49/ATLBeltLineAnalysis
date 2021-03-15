## BeltlineAnalysis
*Atlanta Beltline Project*
Zach Doernberg, Katherine Lee, Sarah Werum, Jake Wylie
May 1, 2020
# 1 Introduction
  This project is in partnership with the Atlanta Beltline and the Preparation for Industrial Careers Math
class at Emory University. For many Atlanta families, transportation is a constant issue. In the Washington
district of Atlanta, families living within a 1.5 mile radius of their high school do not receive school-provided
transportation and are therefore tasked with finding their own mode of travel to and from school. With Atlanta
lacking much public transportation, students must be either driven to school or will end up walking. This is
an issue especially for lower income families that cannot afford - either due to money or time - to drive their
children to and from school. The Beltline is a sustainable redevelopment project that will ultimately connect 45
in town neighborhoods via a 22-mile loop of multi-use trails, modern streetcars, and parks – all based on railroad
corridors that formerly encircled Atlanta and, as one of the largest urban revitalization efforts in Atlanta, is
attempting to provide an alternative solution for the community.
  Booker T. Washington High School stands out because of its geographical intersection with the Beltline.
Because of its proximity to the Westside trail of the Beltline and because the Beltline runs through its school
district, we have decided to focus on how high schoolers enrolled in Booker T. Washington High School may be
able to utilize the Beltline on their way to school.
  Working with spatial data, we have worked to identify optimal walking routes to Washington High School
that utilize the already existing Atlanta Beltline and offer suggestions for access points on its planned extension
to the north based on our findings. Using street and sidewalk networks, the Beltline access points, neighborhood
data, and tax parcel data, we are attempting to provide the best walking route for these students to get to
school safely. We hope that our results will be able to support the Beltline’s efforts to incorporate Safe Routes
to School(SRTS), a national initiative designed to improve the safety and physical well-being of students, into
its planning activities. Thus, we aim to find more safe and optimal routes to school, while also guiding urban
design decision-making for the city of Atlanta.
# 2 Results
  Using differing weight functions, we were able to determine which streets would be most used by students
getting to school. However, the results we get differ based on how we weigh our different parameters. These
parameters include distance, road types, the Beltline, and the existence of a sidewalk. We wrote our cost
function to prefer the Beltline and, when deciding between streets, to pick less-used streets. The below map
marks the different neighborhoods’ paths - in red - to the school(red rectangle). The paths are drawn translucent
and on top of each other, so more frequently taken streets are marked in a darker red. Black dots indicate the
center of a neighborhood. Then, the light pink route looping in the North represents the Beltline. Finally, the
axes surrounding the map represent geographical coordinates.
1Figure 1: Paths to Booker T Washington High School Prioritizing Sidewalks, the Beltline, and Road Type
  Using this map, we can identify which streets are most used by students to walk to school and especially
which paths are used to utilize the Beltline. Unsurprisingly, the streets between the high school and the Beltline
are used a lot, but there are several streets which are also frequently used in our algorithm. One application of
our results, if our industry partner chooses, can be an effort to improve existing infrastructure in areas of high
frequency. For example, by looking closely at our results we can see that Lucile Avenue, Cascade Avenue and
S Gordon Street, which cross the Beltline to the South of the high school, are three such streets.
# 2.1 Give Details On Problem Approach
  Our approach to this problem is a weighted path A* algorithm. The A* algorithm is highly regarded in
path-traversal due to thoroughness and optimality. We can manipulate our weight function to consider different
factors. We have found Python to be a useful tool for implementing these algorithms in our project.
  For the A* algorithm, we will use a Hash Map, also known as a dictionary in python. This data structure
holds key-value pairs. In our case the keys will be represented by the coordinate street intersections and the
values will be the street segment between the coordinates and a heuristic. Conceptually, we can think of the
coordinates as nodes of a graph and the roads between each coordinate as the path. For each of these nodes we
can use a function to get all the vertices connected to the current node via a street segment. Every node will
also have a heuristic. A heuristic is an approximation of future cost. The heuristic we use is the straight line
distance to the high school. Finally, we need a weight function to determine the weight of the path between two
vertices. This is where we would implement factors such as sidewalk availability, street size, and safety into our
path selection. For any two vertices, our weight function will return the cost of the road segment we’re taking.
  The A* algorithm works by weighing all the path options available to it, by adding the heuristic of the
leading node and the weights of the paths we take to get there. For example, in Figure 2, we start by adding
the heuristic of our start node in the top left to the two paths available to us- getting 3+3=6 and 4+3=7 - and
then move along the path with the lower cost. We will keep track of our path options in a priority queue, so
that we can always select the path with the lowest current cost. A priority queue is a data structure that sorts
its entries, so that you can continuously remove its smallest element.
2Figure 2: Map Example
  The numbers in the nodes represent the heuristic as the Manhattan distance, the numbers along the edges
represent each edge’s weight function.
  Using the top-left node with heuristic 4, we identify two ways forward: One using edge 3 and one using
edge 4, so we add the heuristic of the next node to the weight and put the sum into our priority queue. Then,
since the path along the horizontal edge has the lower value(3+3=6), we move along that path to the vertex
with heuristic 3. We then get the next available nodes from the current node with heuristic(3) along the top
horizontal path giving the node with heuristic(2) and add the sum of the weights to along and the heuristic and
add it to the priority queue. Now we have two items in our priority queue, whose values are 7 and 11, so we
continue with the vertex whose value is 7. We then get the next available nodes, giving us the node to its right
with heuristic(2) and add the sum of the weights and the heuristic. So a value of 7 goes on the priority queue.
Then, since 7 is still less than 11, we continue to the next vertex from there. However, it has two new outgoing
paths, so we add two new items to our priority queue: heuristic(1)+weights (4 + 1 + 4) = 10 and heuristic(1)+weights (4 + 1 + 2) = 8. We again continue with the smallest value in our priority queue(8) and move to its
next vertex - the rightmost vertex with heuristic one. Here we add the heuristic(0) to the weights(4+1+2+2)
= 9. Since this is still the smallest value in our priority queue, we move to the next vertex again and get to our
end vertex with heuristic 0. Thus, the shortest path is the one taking edges 4, 1, 2, and 2.
  We could then run this algorithm for all of our parcels, but this would be a tremendous amount of information
to process and a very large output we would get back, so instead we decided to split up our parcel data by
neighborhood code. Our weight function will take into account three factors: the existence of a sidewalk, the
type of road, and distance. The Georgia Department of Transportation distinguishes between 4 types of roads
in our data set: Local, Collector, Minor Arterial, and Major Arterial. Using this distinction, we can give most
priority to Local Roads and least to Major Arterials, which will have the highest motor vehicle traffic and speed
limits.
  This algorithm,once completed, will act as an incredibly versatile tool. Inspired by the “Spaghetti plots”
used by meteorologists, we run this algorithm several times with slightly different weight functions.
# 2.2 More Detailed Results
  Using differing weight functions, we were able to determine which streets would be most used by students
getting to school. However, the results we get differ based on how we weigh our different parameters.
3Figure 3: Paths to Booker T Washington High School by Distance
We started with a weight function that incorporated only the distance of the path. In this map, we can
already see several neighborhoods for whom it would not make sense to go to school on the Beltline. These
consist of the neighborhoods to the North and to the East of Booker T. Washington high school. Neighborhoods
to the South do not necessarily use the Beltline, but they are close enough to it that it is possible, even though
it may not be the shortest path in terms of distance
Figure 4: Paths to Booker T Washington High School Prioritizing the Beltline
  Our next function however, adds one to our distance for every step from one coordinate to the next we take,
if we are not on the Beltline, which incentivises our algorithm to search for paths utilizing the Beltline. In this
map, we can see several neighborhoods to the South and Southeast of the high school being redirected onto the
Beltline. Especially in the far south, neighborhoods may be very close to the Beltline, but it takes them on a
roundabout way, so this path was not considered when we were calculating our paths strictly on distance.
4Figure 5: Paths to Booker T Washington High School Prioritizing the Beltline, Streets with Sidewalks and
Road Types
  Our final figure takes into account not only the Beltline but the existence of a sidewalk and the road type
the student would be walking on. Similarly to our Beltline weighing, we simply add a factor to each step taken
on our path to incentivise taking sidewalks and road types with less traffic and lower speed limits. With this
final version of our algorithm 18 of our neighborhoods use the Beltline in some capacity. The percentages of
the path traveled on the Beltline for these neighborhoods is outlined in Table 3 in the appendix. Streets with
no sidewalks gain a cost of one per step. The weights assigned to the road types are as follows:
Table 1. Table of Road Type Penalties
  These modifications do not greatly influence students’ use of the Beltline. However, they still improve their
paths to school. We can see this map’s difference to its predecessor especially in the paths chosen for the
neighborhoods to the East and Northeast. Paths utilizing the Beltline will reduce their path lengths by moving
on the Beltline more. However, the paths that do not utilize the Beltline can improve their paths by making
these smaller improvements.
5Figure 6: Closeup on Southwest for Path to Booker T Washington High School Prioritizing the Beltline,
Sidewalks, and Road Types
  In this closeup of the paths utilizing the Westside trail of the Beltline, we can identify several roads that
are instrumental for students to get to the Beltline. Firstly, three neighborhoods utilize Lucile Avenue SW,
which we see on this map west of the eastward curve of the Beltline running west, orthogonal to the Beltline.
Similarly, south of Lucile Avenue and going off to the east, we have Cascade Avenue SW and S Gordon Street
SW.
Figure 7: Closeup on Northwest for Path to Booker T Washington high school prioritizing the Beltline,
Sidewalks, and Road Type
  To the North of Booker T Washington high school, Lena Street NW is especially well-used, as well as
Burbank Dr NW. Noticeably, the neighborhoods to the Northwest of the high school are rather close to the
northward extension of the Beltline, making the crossing of the Beltline and Joseph E. Boone Boulevard NW
6a possible location for an access point. Similarly, in the Northeast of this map, there is one neighborhood
path that does not utilize the Beltline, but is very close to the Northside extension, so the students in that
neighborhood could use the Beltline if we were to add an access point nearby. The aforementioned possible
access points are marked on this map with black stars. As the project continued, we wrestled with the incorporation of different data into our cost function. After deliberation on the topic of crime and safety, we decided that crime data would both be challenging to implement and perhaps not the most useful data, due to the
prevalence of property crimes over violent crimes. We do, however, acknowledge the need for incorporating a
safety component. We integrated the safety component based on two considerations: speed limit ranges and a
High Injury Network. According to the Atlanta Regional Commission’s ‘Walk.Bike.Thrive!’ Initiative, the data
show that approximately 70% of pedestrian-involved crashes occur at speed limits 35mph or higher. With this
being said, the true crux of the project appears to be: where is the trade off between distance/time traveled and
safety? Ideally, we want to prioritize streets with speed limits lower than 35mph. We used average speed limits
and generalized it to our map, given that more specific data on speed limits was not available to us. Thus, we
acknowledge there are some exceptions to the road type and speed limits connections. Based on our research,
the average speed limits of local and collector roads in the area tended to be below 35mph. One important
distinction to make is that research suggests speed limits on collectors range from 30-55mph. Upon inspection,
the majority of the collectors in the Washington district had speed limits between 30-35mph. With that in
mind, we decided to group these two road types together and prioritize them, while avoiding arterials which
tend to be over 50mph. The road type, speed limit, and associated cost are outlined in Table 2. Following
these results, we sought a more profound understanding of the safety in this area, one that did not rely solely
on speed limit averages. With the help of our industry partner, we obtained data from a ‘High Injury Network(HIN)’ which traffic accident data presented to us as spatial data. By incorporating the HIN, we gleaned more insight into problematic intersections in our district. It became apparent that the HIN showed a higher
proportion of accidents on certain types of roads, namely collectors and minor arterials. These findings corroborated the motivation to avoid arterial roads, while also bringing to our attention the need to avoid collector roads. The costs associated with both the High Injury Network and the speed limit are also displayed in Table 2.
Table 2. Road Type, Speed Limit, and New Penalties
7Figure 8: Speed Limit weighted Paths to Booker T Washington High School
Figure 9: HIN and Speed Limit Weighted Paths to Booker T Washington High School
# 3 Conclusion and Future Work
  We do not have a single result. Rather, the reader themselves must decide which parameters they deem
most important: safety or distance. Both are important factors, but we must sometimes sacrifice a shorter
walking distance for a more safe path and vice versa. We have also identified which infrastructure will be
particularly useful in order for students of Booker T. Washington high school to get to the Beltline. However,
more importantly, we have created an invaluable tool that can be re purposed for similar projects. If the Beltline
decides to repeat this project with other schools, our algorithm could be easily adapted to new sets of data, for
example to find paths for students of Carver high school in Atlanta.
  Future research and implementation of our project can be carried out, not just on different schools, but
8also with varying weights depending on the information available. For example, our current weight function
takes into account distance, sidewalks, road types and the Beltline, however, it could be modified to incorporate
crime data or street-specific speed limits. There is also the option in the future to incorporate the undeveloped
sections of the Beltline to see how the optimal paths then change. With newfound data, the potential to create
an even more rigorous output of optimal paths is made feasible by our algorithm.
# 4 Acknowledgments
  PIC Math is a program of the Mathematical Association of America (MAA). Support for this MAA program
is provided by the National Science Foundation (NSF grant DMS-1722275) and the National Security Agency (NSA)
Dr. Bree Ettinger
Atlanta Beltline Inc.
# 5 References
Atlanta Regional Commission (ARC)
Speed Limit Data
# 6 Appendix
Table 3. Neighborhoods with Percentage of Path on Beltline
9Code Segment 1: A* Algorithm
def a S t a r S e a r c h ( s t a r t s t a t e , g o a l s t a t e ) :
s t a r t = s t a r t s t a t e
v i s i t e d = [ ]
p a th s = [ ]
f r i n g e = u t i l . p ri o ri t yQ u e u e ( )
f r i n g e . push ( ( s t a r t , [ ] ) , h e u r i s t i c ( s t a r t s t a t e , g o a l s t a t e ) )
while not f r i n g e . isEmpty ( ) :
p r i o r i t y , node = f r i n g e . pop ( )
s t a t e = node [ 0 ]
moves = node [ 1 ]
i f s t a t e == g o a l s t a t e :
moves = moves + [ s t a t e ]
return moves , v i s i t e d , f r i n g e
i f s t a t e not in v i s i t e d :
fo r c h i l d in g e tN e x tP oi n t s ( s t a t e ) :
i f not c h i l d in v i s i t e d :
newNode = ( c hil d , moves + [ s t a t e ] )
c o s t = ge tC o s t ( newNode [ 1 ] + [ c h i l d ] ) +
h e u r i s t i c ( newNode [ 0 ] , g o a l s t a t e )
f r i n g e . push ( ( c hil d , moves + [ s t a t e ] ) , c o s t )
v i s i t e d . append ( s t a t e )
return moves , v i s i t e d , f r i n g e
u t i l . r ai s e N o tD e fi n e d ( )
Code Segment 2: Cost Function Used by A* Algorithm
def ge tC o s t ( moves ) :
c o s t = 0
10fo r i in range ( len ( moves ) − 1 ) :
# d i s t a n c e c o s t
d i f f x = moves [ i ] [ 0 ] − moves [ i + 1 ] [ 0 ]
d i f f y = moves [ i ] [ 1 ] − moves [ i + 1 ] [ 1 ]
a u x di s t = math . s q r t ( ( d i f f x ∗∗ 2 ) + ( d i f f y ∗∗ 2 ) )
a u x di s t = a u x di s t /5280
# b e l t l i n e b e n e f i t
i f moves [ i ] in u t i l . b e l t l i n e p o i n t s or moves [ i +1] in u t i l . b e l t l i n e p o i n t s :
c o s t += a u x di s t
e l s e :
c o s t += a u x di s t + 1
# g e t t y p e c o s t
i f ( moves [ i ] , moves [ i +1]) in u t i l . segments . key s ( ) :
t y p e c o s t = getTypeCost ( u t i l . segments [ ( moves [ i ] , moves [ i + 1 ] ) ] [ 2 ] ) ∗ 1
c o s t += t y p e c o s t
e l i f ( moves [ i +1] , moves [ i ] ) in u t i l . segments . key s ( ) :
t y p e c o s t = getTypeCost ( u t i l . segments [ ( moves [ i +1] , moves [ i ] ) ] [ 2 ] ) ∗ 1
c o s t += t y p e c o s t
# s i d e w a l k c o s t
i f ( moves [ i ] , moves [ i +1]) in u t i l . segments . key s ( ) :
i f u t i l . segments [ ( moves [ i ] , moves [ i + 1 ] ) ] [ 4 ] == F al s e :
c o s t += 1
e l i f ( moves [ i +1] , moves [ i ] ) in u t i l . segments . key s ( ) :
i f u t i l . segments [ ( moves [ i +1] , moves [ i ] ) ] [ 4 ] == F al s e :
c o s t += 1
Note: Lines prefaced by a # are comments for the reader only. They are not read as part of the code
