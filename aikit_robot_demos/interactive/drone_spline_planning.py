# global
import os
import aikit
import time
import argparse
import aikit_mech
import aikit_robot
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from aikit_robot.rigid_mobile import RigidMobile
from aikit_demo_utils.aikit_scene.scene_utils import BaseSimulator


class Simulator(BaseSimulator):
    def __init__(self, interactive, try_use_sim):
        super().__init__(interactive, try_use_sim)

        # aikit robot
        rel_body_points = aikit.array(
            [
                [0.0, 0.0, 0.0],
                [-0.15, 0.0, -0.15],
                [-0.15, 0.0, 0.15],
                [0.15, 0.0, -0.15],
                [0.15, 0.0, 0.15],
            ]
        )
        self.aikit_drone = RigidMobile(rel_body_points)

        # initialize scene
        if self.with_pyrep:
            self._spherical_vision_sensor.remove()
            for i in range(6):
                self._vision_sensors[i].remove()
                self._vision_sensor_bodies[i].remove()
                [ray.remove() for ray in self._vision_sensor_rays[i]]
            drone_start_pos = aikit.array([-1.15, -1.028, 0.6])
            target_pos = aikit.array([1.025, 1.125, 0.6])
            self._drone.set_position(drone_start_pos)
            self._drone.set_orientation(aikit.array([-90, 50, -180]) * aikit.pi / 180)
            self._target.set_position(target_pos)
            self._target.set_orientation(aikit.array([-90, 50, -180]) * aikit.pi / 180)
            self._default_camera.set_position(aikit.array([-3.2835, -0.88753, 1.3773]))
            self._default_camera.set_orientation(
                aikit.array([-151.07, 70.079, -120.45]) * aikit.pi / 180
            )

            input(
                "\nScene initialized.\n\n"
                "The simulator visualizer can be translated "
                "and rotated by clicking either the left mouse button or the wheel, "
                "and then dragging the mouse.\n"
                "Scrolling the mouse wheel zooms the view in and out.\n\n"
                "You can click on any object either "
                "in the scene or the left hand panel, "
                "then select the box icon with four arrows "
                "in the top panel of the simulator, "
                "and then drag the object around dynamically.\n"
                "Starting to drag and then holding ctrl allows you "
                "to also drag the object up and down.\n"
                "Clicking the top icon with a box and "
                "two rotating arrows similarly allows rotation "
                "of the object.\n\n"
                "Once you have aranged the scene as desired, "
                "press enter in the terminal to continue with the demo...\n"
            )

            # primitive scene
            self.setup_primitive_scene()

            # public objects
            drone_starting_inv_ext_mat = aikit.array(
                self._drone.get_matrix()[0:3].tolist(), dtype="float32"
            )
            drone_start_rot_vec_pose = aikit_mech.mat_pose_to_rot_vec_pose(
                drone_starting_inv_ext_mat
            )
            self.drone_start_pose = drone_start_rot_vec_pose
            target_inv_ext_mat = aikit.array(
                self._target.get_matrix()[0:3].tolist(), dtype="float32"
            )
            target_rot_vec_pose = aikit_mech.mat_pose_to_rot_vec_pose(target_inv_ext_mat)
            self.drone_target_pose = target_rot_vec_pose

            # spline path
            drone_start_to_target_poses = aikit.permute_dims(
                aikit.linspace(self.drone_start_pose, self.drone_target_pose, 100),
                axes=(1, 0),
            )
            drone_start_to_target_inv_ext_mats = aikit_mech.rot_vec_pose_to_mat_pose(
                drone_start_to_target_poses
            )
            drone_start_to_target_positions = aikit.permute_dims(
                self.aikit_drone.sample_body(drone_start_to_target_inv_ext_mats),
                axes=(1, 0, 2),
            )
            initil_sdf_vals = aikit.reshape(
                self.sdf(
                    aikit.reshape(
                        aikit.astype(drone_start_to_target_positions, "float32"), (-1, 3)
                    )
                ),
                (-1, 100, 1),
            )
            self.update_path_visualization(
                drone_start_to_target_positions, initil_sdf_vals, None
            )

            # wait for user input
            self._user_prompt(
                "\nInitialized scene with a drone and a target position to reach."
                "\nPress enter in the terminal to "
                "use method aikit_robot.interpolate_spline_points "
                "to plan a spline path which reaches the target "
                "whilst avoiding the objects in the scene...\n"
            )

        else:
            # primitive scene
            self.setup_primitive_scene_no_sim()

            # public objects
            self.drone_start_pose = aikit.array(
                [-1.1500, -1.0280, 0.6000, 0.7937, 1.7021, 1.7021]
            )
            self.drone_target_pose = aikit.array(
                [1.0250, 1.1250, 0.6000, 0.7937, 1.7021, 1.7021]
            )

            # message
            print(
                "\nInitialized dummy scene with a drone and "
                "a target position to reach."
                "\nClose the visualization window to use "
                "method aikit_robot.interpolate_spline_points "
                "to plan a spline path which reaches the target "
                "whilst avoiding the objects in the scene...\n"
            )

            # plot scene before rotation
            if interactive:
                plt.imshow(
                    mpimg.imread(
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            "dsp_no_sim",
                            "path_0.png",
                        )
                    )
                )
                plt.show()

        print("\nOptimizing spline path...\n")

    def execute_motion(self, poses):
        print("\nSpline path optimized.\n")
        if self._interactive:
            input("\nPress enter in the terminal to execute motion.\n")
        print("\nExecuting motion...\n")
        if self.with_pyrep:
            for i in range(100):
                pose = poses[i]
                inv_ext_mat = aikit_mech.rot_vec_pose_to_mat_pose(pose)
                self._drone.set_matrix(
                    aikit.to_numpy(aikit_mech.make_transformation_homogeneous(inv_ext_mat))
                )
                time.sleep(0.05)
        elif self._interactive:
            this_dir = os.path.dirname(os.path.realpath(__file__))
            for i in range(11):
                plt.ion()
                plt.imshow(
                    mpimg.imread(
                        os.path.join(this_dir, "dsp_no_sim", "motion_{}.png".format(i))
                    )
                )
                plt.show()
                plt.pause(0.1)
                plt.ioff()


# Cost Function


def compute_length(query_vals):
    start_vals = query_vals[0:-1]
    end_vals = query_vals[1:]
    dists_sqrd = aikit.maximum((end_vals - start_vals) ** 2, 1e-12)
    distances = aikit.sum(dists_sqrd, axis=-1) ** 0.5
    return aikit.sum(distances)


def compute_cost_and_sdfs(
    learnable_anchor_vals,
    anchor_points,
    start_anchor_val,
    end_anchor_val,
    query_points,
    sim,
):
    anchor_vals = aikit.concat(
        (
            aikit.expand_dims(start_anchor_val, axis=0),
            learnable_anchor_vals,
            aikit.expand_dims(end_anchor_val, axis=0),
        ),
        axis=0,
    )
    poses = aikit_robot.sample_spline_path(anchor_points, anchor_vals, query_points)
    inv_ext_mat_query_vals = aikit_mech.rot_vec_pose_to_mat_pose(poses)
    body_positions = aikit.permute_dims(
        sim.aikit_drone.sample_body(inv_ext_mat_query_vals), axes=(1, 0, 2)
    )
    length_cost = compute_length(body_positions)
    sdf_vals = sim.sdf(aikit.reshape(body_positions, (-1, 3)))
    coll_cost = -aikit.mean(sdf_vals)
    total_cost = length_cost + coll_cost * 10
    return total_cost, poses, body_positions, aikit.reshape(sdf_vals, (-1, 100, 1))


def main(interactive=True, try_use_sim=True, fw=None):
    # config
    this_dir = os.path.dirname(os.path.realpath(__file__))
    fw = aikit.choose_random_backend(excluded=["numpy"]) if fw is None else fw
    aikit.set_backend(fw)
    sim = Simulator(interactive, try_use_sim)
    lr = 0.05
    num_anchors = 3
    num_sample_points = 100

    # 1D spline points
    anchor_points = aikit.astype(
        aikit.expand_dims(aikit.linspace(0, 1, 2 + num_anchors), axis=-1), "float32"
    )
    query_points = aikit.astype(
        aikit.expand_dims(aikit.linspace(0, 1, num_sample_points), axis=-1), "float32"
    )

    # learnable parameters
    drone_start_pose = aikit.astype(aikit.array(sim.drone_start_pose), "float32")
    target_pose = aikit.astype(aikit.array(sim.drone_target_pose), "float32")
    learnable_anchor_vals = aikit.astype(
        aikit.permute_dims(
            aikit.linspace(drone_start_pose, target_pose, 2 + num_anchors)[..., 1:-1],
            axes=(1, 0),
        ),
        "float32",
    )

    # optimizer
    optimizer = aikit.SGD(lr=lr)

    # optimize
    it = 0
    colliding = True
    clearance = 0.1
    poses = None
    while colliding and it < 13:
        func_ret, grads = aikit.execute_with_gradients(
            lambda xs: compute_cost_and_sdfs(
                xs, anchor_points, drone_start_pose, target_pose, query_points, sim
            ),
            learnable_anchor_vals,
            ret_grad_idxs=["0"],
        )

        poses = func_ret[1]
        body_positions = func_ret[2]
        sdf_vals = func_ret[3]

        colliding = aikit.min(sdf_vals) < clearance
        sim.update_path_visualization(
            body_positions,
            sdf_vals,
            os.path.join(this_dir, "dsp_no_sim", "path_{}.png".format(it)),
        )
        learnable_anchor_vals = optimizer.step(learnable_anchor_vals, grads["0"])
        it += 1
    sim.execute_motion(poses)
    sim.close()
    aikit.previous_backend()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--non_interactive",
        action="store_true",
        help="whether to run the demo in non-interactive mode.",
    )
    parser.add_argument(
        "--no_sim",
        action="store_true",
        help="whether to run the demo without attempt to use the PyRep simulator.",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=None,
        help="which backend to use. Chooses a random backend if unspecified.",
    )
    parsed_args = parser.parse_args()
    fw = parsed_args.backend
    main(not parsed_args.non_interactive, not parsed_args.no_sim, fw)
