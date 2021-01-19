# Author: Zi Wang
import kitchen2d.kitchen_stuff as ks
from kitchen2d.kitchen_stuff import Kitchen2D
from kitchen2d.gripper import Gripper
import numpy as np
import time
from copy import copy

SETTING = {
    'do_gui': False,
    'sink_w': 10.,
    'sink_h': 5.,
    'sink_d': 1.,
    'sink_pos_x': 20.,
    'left_table_width': 50.,
    'right_table_width': 50.,
    'faucet_h': 12.,
    'faucet_w': 5.,
    'faucet_d': 0.5,
    'planning': False,
    'overclock': 50 # number of frames to skip when showing graphics.
}

def query_gui(action_type, kitchen):
    choice = raw_input('Show GUI for {}? [y/n]'.format(action_type))
    if choice == 'y':
        print('Enabling GUI...')
        kitchen.enable_gui()
    else:
        print('Disabling GUI...')
        kitchen.disable_gui()

class BPSim():
    """
    Abstraction of Kitchen2D simulation to fit symbolic planning via BP Planner.
    """
    def __init__(self, gripper_init_pos=(20,40), gripper_init_angle=0):
        """
        Input(s):
            gripper_init_pos: (int, int),
            gripper_init_angle: int
        """
        self.kitchen = Kitchen2D(**SETTING)
        self.gripper = Gripper(self.kitchen, gripper_init_pos, gripper_init_angle)
        self.symbol_to_obj = {}

    def move_drawer(self, drawer_sym, drop_pos=(-10, 10)):
        """
        Move `drawer_sym` out of the way and drop it at `drop_pos`.
        """
        query_gui('MOVE_DRAWER', self.kitchen)
        grasp = 0.306249162768 # tunable parameter for path planner
        drawer_obj = self.symbol_to_obj[drawer_sym]
        drawer_pos = drawer_obj.position

        self.gripper.find_path((drawer_pos[0], drawer_pos[1] + 10), 0)
        self.gripper.grasp(drawer_obj, grasp)

        self.gripper.find_path((drop_pos[0], drop_pos[1] + 10), 0)
        self.gripper.place(drop_pos, 0)

    def pick_up(self, obj_sym):
        """
        Pick up object represented by `obj_sym` in simulation.
        """
        query_gui('PICK_UP', self.kitchen)
        grasp = 0.306249162768 # tunable parameter for path planner
        obj = self.symbol_to_obj[obj_sym]
        obj_pos = obj.position
        self.gripper.find_path((obj_pos[0], obj_pos[1] + 10), 0)
        self.gripper.grasp(obj, grasp)

    def place(self, pos):
        """
        Place held object at position `pos`.
        """
        query_gui('PLACE', self.kitchen)
        self.gripper.place(pos, 0)

    def fill(self, duration=1):
        """
        Fill held object with water for `duration` seconds
        """
        query_gui('FILL', self.kitchen)
        self.gripper.get_liquid_from_faucet(duration)

    def pour(self, obj_sym):
        """
        Pour liquid into object represented by `obj_sym`.
        """
        query_gui('POUR', self.kitchen)
        grasp = 0.306249162768
        rel_x = 3.70183788428
        rel_y = 9.01263886707
        dangle = 1.59620914618
        dangle *= np.sign(rel_x)
        obj = self.symbol_to_obj[obj_sym]
        print(self.gripper.pour(obj, (rel_x, rel_y), dangle))
        # After every pour, place the object
        self.gripper.place((obj.position[0]+ obj.usr_w + 1, 0), 0)

    def scoop(self, obj_sym, spoon_sym, dump_sym, spoon_grasp_pos=(23, 10), drop_pos=(0,10)):
        """
        Grasp `spoon_sym`, scoop from `obj_sym`, dump contents into `dump_sym`.
        """
        query_gui('SCOOP', self.kitchen)
        # Tunable parameters received from the active sampling method
        rel_x1 = 0.0276296492162
        rel_y1 = 0.611922721287
        rel_x2 = 0.846900041891
        rel_y2 = 0.056968220054
        rel_x3 = 0.960750333945
        rel_y3 = 0.126499043204
        grasp = 0.883195866437
        rel_pos1 = (rel_x1, rel_y1); rel_pos2 = (rel_x2, rel_y2); rel_pos3 = (rel_x3, rel_y3)

        spoon = self.symbol_to_obj[spoon_sym]
        obj = self.symbol_to_obj[obj_sym]
        dump = self.symbol_to_obj[dump_sym]

        self.gripper.set_grasped(spoon, grasp, spoon_grasp_pos, 0)
        print(self.gripper.scoop(obj, rel_pos1, rel_pos2, rel_pos3))

        # Dumping contents of scoop
        self.gripper.dump(dump, 0.9) # 0.9 is tunable

        # Placing spoon
        self.gripper.place(drop_pos, 0)

    def stir(self, stir_sym, obj_sym, stir_grasp_pos=(10,10), num_stirs=5):
        """
        Pick up `stir_sym` and stir in `obj_sym`.
        `stir_grasp_pos`: position of gripper after picking up stirrer
        `num_stirs`: number of times to stir inside `obj_sym`
        """
        query_gui('STIR', self.kitchen)        
        stirrer = self.symbol_to_obj[stir_sym]
        obj = self.symbol_to_obj[obj_sym]
        
        self.gripper.set_grasped(stirrer, 0.8, stir_grasp_pos, 0)
        self.gripper.stir(obj, (0, 0.0), (1, 0.0), num_stirs=num_stirs)
        self.gripper.find_path(self.gripper.position + [0, 5], 0)

    def init_mapping(self, registry):
        """
        Creates mapping of symbol to object.
        """
        self.symbol_to_obj = copy(registry)

def build_world(bp_sim):
    """
    Returns tuple of objects in world.
    """
    # Preset parameters that make this effective
    pour_to_w = 4.17393549546
    pour_to_h = 4.05998671658
    pour_from_w = 3.61443970857
    pour_from_h = 4.51052132521

    scoop_w = 5.388370713
    scoop_h = 4.52898336641
    holder_d = 0.5

    cup1_x = -20
    cup2_x = 0
    large_cup_x = 10

    # Create objects
    drawer1 = ks.make_drawer(bp_sim.kitchen, (cup1_x, pour_from_h+2), 0, pour_from_w*2 + 2.5*holder_d, pour_from_h, holder_d)
    cup1 = ks.make_cup(bp_sim.kitchen, (cup1_x,0), 0, pour_from_w, pour_from_h, holder_d)
    drawer2 = ks.make_drawer(bp_sim.kitchen, (cup2_x, pour_from_h+2), 0, pour_from_w*2 + 2.5*holder_d, pour_from_h, holder_d)
    cup2 = ks.make_cup(bp_sim.kitchen, (cup2_x,0), 0, pour_to_w, pour_to_h, holder_d)
    large_cup = ks.make_cup(bp_sim.kitchen, (large_cup_x, 0), 0, scoop_w, scoop_h, holder_d)

    return drawer1, cup1, drawer2, cup2, large_cup

def main():
    bp_sim = BPSim()

    # Example 
    sym_list = ['drawer1', 'cup1', 'drawer2', 'cup2', 'large_cup']
    obj_list = build_world(bp_sim)
    bp_sim.init_mapping(dict(zip(sym_list, obj_list)))

    # Actions
    bp_sim.move_drawer('drawer1')

if __name__ == '__main__':
    main()

# def main():
#     kitchen = Kitchen2D(**SETTING)

#     # Preset parameters that make this effective
#     pour_to_w = 4.17393549546
#     pour_to_h = 4.05998671658
#     pour_from_w = 3.61443970857
#     pour_from_h = 4.51052132521

#     scoop_w = 5.388370713
#     scoop_h = 4.52898336641
#     holder_d = 0.5

#     cup1_x = -20
#     cup2_x = 0
#     large_cup_x = 10

#     # Create objects
#     gripper = Gripper(kitchen, (20,40), 0)
#     drawer1 = ks.make_drawer(kitchen, (cup1_x, pour_from_h+2), 0, pour_from_w*2 + 2.5*holder_d, pour_from_h, holder_d)
#     cup1 = ks.make_cup(kitchen, (cup1_x,0), 0, pour_from_w, pour_from_h, holder_d)
#     drawer2 = ks.make_drawer(kitchen, (cup2_x, pour_from_h+2), 0, pour_from_w*2 + 2.5*holder_d, pour_from_h, holder_d)
#     cup2 = ks.make_cup(kitchen, (cup2_x,0), 0, pour_to_w, pour_to_h, holder_d)
#     large_cup = ks.make_cup(kitchen, (large_cup_x, 0), 0, scoop_w, scoop_h, holder_d)
    
#     # Move
#     query_gui('MOVE', kitchen)
#     gripper.find_path((-5., 10), 0, maxspeed=0.5)

#     # Pick
#     query_gui('GRASP', kitchen)
#     grasp = 0.306249162768
#     rel_x = 3.70183788428
#     rel_y = 9.01263886707
#     dangle = 1.59620914618
#     dangle *= np.sign(rel_x)

#     gripper.find_path((cup1_x, 10), 0)
#     gripper.grasp(drawer1, grasp)

#     query_gui('PLACE', kitchen)
#     gripper.find_path((2, 10), 0)

#     gripper.place((-10, 10), 0)

#     query_gui('GRASP', kitchen)
#     gripper.find_path((cup1_x, 10), 0)
#     gripper.grasp(cup1, grasp)

#     query_gui('GET-WATER', kitchen)
#     gripper.get_liquid_from_faucet(1) # 5 true

#     # Pour
#     query_gui('POUR', kitchen)
#     print(gripper.pour(cup2, (rel_x, rel_y), dangle))

#     # Place
#     query_gui('PLACE', kitchen)
#     print("cup2 position: {cup2.position}")
#     gripper.place((cup2.position[0]+ cup2.usr_w + 1, 0), 0)

#     # Scoop
#     kitchen.gen_liquid_in_cup(large_cup, 50, 'sugar') # 1000 true
#     kitchen.gen_liquid_in_cup(cup1, 50) # 200 true
#     spoon = ks.make_spoon(kitchen, (23, 10), 0, 0.2, 3, 1.)

#     query_gui('SCOOP', kitchen)
#     rel_x1 = 0.0276296492162
#     rel_y1 = 0.611922721287
#     rel_x2 = 0.846900041891
#     rel_y2 = 0.056968220054
#     rel_x3 = 0.960750333945
#     rel_y3 = 0.126499043204
#     grasp = 0.883195866437

#     rel_pos1 = (rel_x1, rel_y1); rel_pos2 = (rel_x2, rel_y2); rel_pos3 = (rel_x3, rel_y3)
#     gripper.set_grasped(spoon, grasp, (23, 10), 0)
#     print(gripper.scoop(large_cup, rel_pos1, rel_pos2, rel_pos3))

#     # Dump
#     query_gui('DUMP', kitchen)
#     gripper.dump(cup1, 0.9)

#     # Place
#     query_gui('PLACE', kitchen)
#     gripper.place((0, 10.), 0)

#     # Grasp
#     query_gui('GRASP', kitchen)
#     gripper.grasp(cup1, grasp)

#     rel_x = 3.70183788428
#     rel_y = 9.01263886707
#     dangle = 1.59620914618
#     dangle *= np.sign(rel_x)
#     # Pour
#     query_gui('POUR', kitchen)
#     print(gripper.pour(cup2, (rel_x, rel_y), dangle))

#     # Stir
#     query_gui('STIR', kitchen)
#     stirrer = ks.make_stirrer(kitchen, (0, 3.5), 0., 0.2, 5., 0.5)
#     gripper.set_grasped(stirrer, 0.8, (10, 10), 0)
#     gripper.stir(cup2, (0, 0.0), (1, 0.0))
#     gripper.find_path(gripper.position + [0, 5], 0)

# TODO
# [x] Test with different arrangement of objects --> parameters unaffected!
# [x] Test with more objects and calls
# [] Add abstraction to fit "API" functionality
# [x] Add "coffee bag", or alternatively, coffee faucet
# [x] Add "drawers" to hide cups and other objects
# [] Change color of setting to become Kitchen for Progress 2D
# [] Clean code to remove unnecessary portions