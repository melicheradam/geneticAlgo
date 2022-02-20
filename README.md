# geneticAlgo

Implementation of genetic algorithm to find the best path on given input map.

### TODO
 - [ ] translate code to english

## assignment description

Let us have a treasure hunter that moves in a world defined by a two-dimensional grid (see picture) and collects treasures that it finds along the way. It starts on the box marked with the letter S and can move in four different directions: up H, down D, right P and left L. It has a finite number of steps. His task is to collect as many treasures as possible. Only a position where the searcher and the treasure are in the same box is considered a treasure hunt. Adjacent fields are not taken into account. 

![obrázok](https://user-images.githubusercontent.com/20504361/154840589-07787b29-bf9b-4ba0-bf13-9c677aadbbbc.png)

## solution

To solve this problem, virtual machine is programmed to traverse the map and generate path.

### Virtual machine

Genetic programming uses a virtual machine. The difference is that we are not looking for a solution directly, but we are looking for a machine setting (memory configuration) that will generate it for us. Such a machine has defined instructions for working with memory, and it changes itself during the run. It generates a solution, and only this solution is evaluated by the fitness function. In this approach, the machine's initial memory is used for crosses and mutations. 

Memory of the machine is set to 64B, where each Byte represents an instruction. Machine ends when machine executes 500 instructions, collects all treasures or escapes bounds of map. 

### Fitness

I have implemented two fitness functions, one takes into account path length, other only number of treasures collected.

![obrázok](https://user-images.githubusercontent.com/20504361/154841188-3b682fc8-dc20-4d7b-b30f-8521198b8d3b.png)

It is clear from the graph that the average journey length is much shorter when using the travel calculation function. The shortest possible path for a given setting is 15, so with my average length of 22 this is a relatively good result out of a hundred attempts. 

### Population & selection methods

Population has defined 5% of elite individuals which are perserved into next generation. Probability of mutations, number of individuals and max number of generations can be defined.

Three methods of selection were tested - roulette, roulette with elitism, my own.
My own method of selection also use elitism there, but in a slightly different way. I store 5% of the population in the field outside the population, but only with a unique solution and the best fitness. These individuals are used for crossing in the creation of each generation, specifically I cross them with 10% of the best individuals in the current population. Until the creation of a new generation, I randomly select the remaining individuals from 75% to 90% of the best individuals in the current population. The upper limit is 90% because I don't want to have many of the same genes there since I already cross the top 10 with the elite. 

Test conditions:
  • Number of generations - 100
  • Number of individuals - 100
  • % chance of mutation - 1.5
  • Map from assignment, start at y: 6, x: 4

I compared the development of average fitness of all individuals in generations. This test was run 100 times, which is an average of 100 times for Generation 1, Generation 2, and so on. These fitness values were, of course, normalized to the interval [0,1]. 

![obrázok](https://user-images.githubusercontent.com/20504361/154841298-307cce1e-d4c8-419a-a38c-5d657a595976.png)

For the sake of interest, I also checked the success of finding a solution during testing. The results of this test are shown in the graph below. 

![obrázok](https://user-images.githubusercontent.com/20504361/154841412-df825b3f-bee7-4e95-b662-4b0e3d5db628.png)

It can be seen that within 100 generations, roulette alone is not able to find a solution. On the other hand, when using elitism, the solution is almost always found. Of course, I didn't think so, so I also tried different mutation settings at Roulette, but even that didn't help the result significantly. 

### Mutations

540 / 5 000
Výsledky prekladov
In finding the optimal mutation, I considered only the two most effective implementations with respect to fitness development. It was my implementation and Roulette with elitism. The test for each mutation value was run 100 times to average the generation in which the solution was found. When the solution was not found, I did not add anything to the average.
Conditions:
  • Number of generations - 200
  • Number of individuals - 100
  • Map from assignment, start at y: 6, x: 4
Whole lines represent generation values, double lines the number not found from the given tests. 

![obrázok](https://user-images.githubusercontent.com/20504361/154841371-9da2eb85-8049-4f86-bdcf-452531224452.png)

The graph shows that the most efficient setting in terms of finding a solution can be achieved using my implementation and a mutation value of 1.5%. Although 2 times out of 100 no solution was found there, it only means that it would be found in later generations. Such a setting would find a solution within an average of 21 generations. 


