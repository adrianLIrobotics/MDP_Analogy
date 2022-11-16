# MDP 1+1 Scenario:

### Scenario:
Given a robot standing in room with task reaching a destination under cartesian coordinates, defined as:
```math
r_{t}=(X_{t},Z_{t},\theta_{t})
```
A default Markov Decision Process is defined such as:


* S = Set of states regarded as the state space. 
* A = Set of actions to transition from one state to another
* P_a(S,S') = Transition probability from state S to state *S'* due *a*. 
*	R_a(S,S') = regard received after transitioning from state *S* to state S' due to *a*.
  
```math
MDP=(S,A,P_a,R_a) 
	
```

### Observations:
* Probability transaction matrix depend on the context. 
* Policies reflect a (hypothesis) reality.

### Scenario 1+1:

* S = { Lost, localized, arrivedDestination }
* A = { Move, Stay, LocalizeInMap, Slam, MoveSlam, StaySlam, MoveLocalizeInMap, StayLocalizeInMap }

_____


