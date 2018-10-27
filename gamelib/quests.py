from __future__ import print_function
import numpy as np
import random
import math
import logging
import time

intros = {
    'lake.png': """
Look at my new invention! It's beautifull.
This new engine will allow you to move
faster than wind! And it is simpler to control.
It is revolutionary!

Do not worry. It has enough fuel.
And repulsion shields are charged.

Touch all the floating cones and go back.
""",
    'sunny.png': """
I talked with Administrator of
Grand Logistics Company.
They want to verify performance and
reliability of new boat.

Let's show them its speed in open sea.

As you can guess the floating spheres indicate
the route or enclose dangerous areas.
""",

    'currents.png': """
Currents are dangerous. Especially near a coast.
Be careful you can lose control when
moving with same speed as the flow.
We need to see how good out 
new boat handle them.
Please return in one piece.
""",

    'long.png': """
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
    'rivers.png': """
Riverland boat racing contest.
""",
    'swamps.png': """
Swampland boat racing contest.
""",
    'irrigation.png': """
Sandland boat racing contest.
""",
    'ice.png': """
Cooland boat racing contest.
""",

    'rescue.png': """
You performing well in these currents.

There is a boat stranded in dangerous area.
We already rescued crew by aiship.
Could you retrieve leaved cargo?
""",
    'curl.png': """
You performing well in these currents.
A strange natural disaster occurred
in a remote region.  We need to see 
if anyone there needs help.
You will do it best.
""",

    'exotic.png': """
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
    'longer.png': """
A bit longer distance.
""",
    'irrigation2.png': """
Sandland boat racing contest was cool!
They prepared a new one.
""",
    'rivers2.png': """
Riverland boat racing contest was cool!
They prepared a new one.
""",

    'lake2.png': """
Thank you for playing Crossing seas!
""",

    'test.png': """

""",
}


def intro_for_level(name):
    return intros.get(name)
