from __future__ import print_function
import numpy as np
import random
import math
import logging
import time

# 0. Depart. (t0) Hilland
# 1. Visit Great Logistics Company HQ (t1) Hilland
# 2. Finish the course around one island (s0,s1) Hilland
# 3. Visit 3 reliability managers. (t1,t2,t3,t4) Hilland
# 4. Finish the route without fuel. (t2,s2,s3) Hilland
# 5. Finish the route with dangerous currents (t3,s4,s5,s6). Sandland
# 6. Find 3 towns with cheap fuel / Make money in limited time (t4,t5,t6,t7,t4). Riverland
# 7. Visit 4 towns to prepare the new Regatta. (t8,t9,t10,t11)Riverland Swampland Sandland Showland
# 8. Race around the continent. (On rails!) (t0,s7,s8,s9) Hilland
# 9. Participate in Regatta. (t1) Hilland
# 10. River race (t12) Riverland
# 11. Swamp race (t13) Swampland
# 12. Channel race (t14) Sandland
# 13. Ice pool race (t15) Showland
# 14. Strange flow. (Alien biology!) (t1, s99) Hilland, Showland
# - Bring the exotic good from a far port. (t4,t16) Riverland, Rainland
# - Rescue crew/goods from stranded! ship. (t3) Sandland
# - Traver around the world. (Sphere!) (t2) Hilland


intros = {
'lake.png' : """
Look at my new invention! It's beautifull.
This new engine will allow you to move
faster than wind! And it is simpler to control.
It is revolutionary!

Do not worry. It has enough fuel.
And repulsion shields are charged.

Touch all the floating cones and go back.
""",
'sunny.png' : """
I talked with Administrator of
Grand Logistics Company.
They want to verify performance and
reliability of new boat.

Let's show them its speed in open sea.

As you can guess the floating spheres indicate
the route or enclose dangerous areas.
""",

'currents.png' : """
Currents are dangerous. Especially near a coast.
Be careful you can lose control when
moving with same speed as the flow.
We need to see how good out 
new boat handle them.
Please return in one piece.
""",

'long.png' : """
The new technology is already being
used for cargo delivery.
Moreover we are preparing the contest.
However, there is another technology that
may be better than ours.
They put my engine on rails!

Let's show how fast the boats
are at long distances.
""",

# group of four
'rivers.png' : """
Riverland boat racing contest.
""",
'swamps.png' : """
Swampland boat racing contest.
""",
'irrigation.png' : """
Sandland boat racing contest.
""",
'ice.png' : """
Cooland boat racing contest.
""",

'rescue.png' : """
You performing well in these currents.

There is a boat stranded in dangerous area.
We already rescued crew by aiship.
Could you retrieve leaved cargo?
""",
'curl.png' : """
You performing well in these currents.
A strange natural disaster occurred
in a remote region.  We need to see 
if anyone there needs help.
You will do it best.
""",

'exotic.png' : """
Unbelievable!
You rescued the crew of alien ship!
They safe now. Alien biology is
very similar to ours. And they have
already shown how to improve our engines

But we need exotic resources that are
only available in one remote country

Please return with it in one piece.
""",

# optional
'longer.png' : """
A bit longer distance.
""",
'irrigation2.png' : """
Sandland boat racing contest was cool!
They prepared a new one.
""",
'rivers2.png' : """
Riverland boat racing contest was cool!
They prepared a new one.
""",

'test.png' : """

""",
}


def intro_for_level(name):
  return intros.get(name)