# MDP 1+1 Scenario:

### Scenario:
Given a robot standing in room with task reaching a destination under cartesian coordinates, defined as:
```math
r_{t}=(X_{t},Z_{t},\theta_{t})
```

The robot can move Up/Down/Left/Right one step at a time in a 2d grid. The robot has a localization algorithm (AMCL) active at all times.

A default Markov Decision Process is defined such as:


* S = Set of states regarded as the state space. 
* A = Set of actions to transition from one state to another
* P_a(S,S') = Transition probability from state S to state *S'* due *a*. 
* R_a(S,S') = regard received after transitioning from state *S* to state S' due to *a*.

Solving the MDP provide us with a policy which maximices reward.
  
```math
MDP=(S,A,P_a,R_a) 
	
```

### Observations:
* Probability transaction matrix depend on the context. 
* Policies reflect a (hypothesis/context) reality.
* There exists future states that are not defined at time t of the mdp.

### Scenario 1+1:

* S = { (x,y,theta,Lost), (x,y,theta,localized)}
* A = { MoveUp, MoveDown, MoveLeft, MoveRight, Stay }

The initial default MDP data for P_a(S,S') and R_a(S,S') can be found [here](https://github.com/adrianLIrobotics/MDP/blob/main/MPD_Data/ThirdDafeultMDP.xlsx)
_____


