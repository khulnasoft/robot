# global
import aikit
import argparse
import aikit_mech
import aikit_robot
import numpy as np
import matplotlib.pyplot as plt
from aikit_robot.manipulator import Manipulator
from aikit_robot.rigid_mobile import RigidMobile

INTERACTIVE = True


def show_2d_spline_path(
    anchor_coords,
    interpolated_coords,
    sc,
    a1c,
    a2c,
    a3c,
    tc,
    x_label,
    y_label,
    title,
    start_label,
    target_label,
):
    if not INTERACTIVE:
        return

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(
        aikit.to_numpy(interpolated_coords[..., 0]).tolist(),
        aikit.to_numpy(interpolated_coords[..., 1]).tolist(),
        s=15,
        c=[[0.2, 0.2, 0.8]],
    )
    ax.scatter(
        aikit.to_numpy(anchor_coords[1:4, 0]).tolist(),
        aikit.to_numpy(anchor_coords[1:4, 1]).tolist(),
        s=80,
        c=[[1.0, 1.0, 1.0]],
        edgecolors=[[0.2, 0.2, 0.8]],
        linewidths=2,
    )
    ax.scatter(
        aikit.to_numpy(anchor_coords[0:1, 0]).tolist(),
        aikit.to_numpy(anchor_coords[0:1, 1]).tolist(),
        s=100,
        c=[[1.0, 0.6, 0.0]],
    )
    ax.scatter(
        aikit.to_numpy(anchor_coords[-1:, 0]).tolist(),
        aikit.to_numpy(anchor_coords[-1:, 1]).tolist(),
        s=100,
        c=[[0.2, 0.8, 0.2]],
    )
    ax.set_xlabel(x_label, size=15)
    ax.set_ylabel(y_label, size=15).set_rotation(0)
    ax.text(sc[0], sc[1], start_label)
    ax.text(a1c[0], a1c[1], "anchor point 1")
    ax.text(a2c[0], a2c[1], "anchor point 2")
    ax.text(a3c[0], a3c[1], "anchor point 3")
    ax.text(tc[0], tc[1], target_label)
    ax.set_title(title)
    ax.axis("equal")
    plt.show()


def show_full_spline_path(
    anchor_poses,
    interpolated_poses,
    sc,
    tc,
    x_label,
    y_label,
    title,
    start_label,
    target_label,
    connect_anchors,
):
    if not INTERACTIVE:
        return

    fig = plt.figure()
    ax = fig.add_subplot(111)

    anchor_poses_trans = aikit.to_numpy(aikit.swapaxes(anchor_poses, 0, 1))
    interpolated_poses_trans = aikit.to_numpy(aikit.swapaxes(interpolated_poses, 0, 1))
    colors = [
        [0.2, 0.2, 0.8],
        [0.8, 0.2, 0.2],
        [0.2, 0.8, 0.8],
        [0.8, 0.2, 0.8],
        [0.8, 0.8, 0.2],
    ]

    if connect_anchors:
        for a_poses in anchor_poses:
            ax.plot(
                aikit.to_numpy(a_poses[:, 0]).tolist(),
                aikit.to_numpy(a_poses[:, 1]).tolist(),
                c=[0.0, 0.0, 0.0],
                linestyle="solid",
                linewidth=3,
            )

    for a_poses, i_poses, col in zip(
        anchor_poses_trans, interpolated_poses_trans, colors
    ):
        ax.scatter(
            aikit.to_numpy(i_poses[..., 0]).tolist(),
            aikit.to_numpy(i_poses[..., 1]).tolist(),
            s=15,
            c=[col],
        )
        ax.scatter(
            aikit.to_numpy(a_poses[1:4, 0]).tolist(),
            aikit.to_numpy(a_poses[1:4, 1]).tolist(),
            s=80,
            c=[[1.0, 1.0, 1.0]],
            edgecolors=[col],
            linewidths=2,
        )

        ax.scatter(
            aikit.to_numpy(a_poses[0:1, 0]).tolist(),
            aikit.to_numpy(a_poses[0:1, 1]).tolist(),
            s=100,
            c=[[1.0, 0.6, 0.0]],
        )

        ax.scatter(
            aikit.to_numpy(a_poses[-1:, 0]).tolist(),
            aikit.to_numpy(a_poses[-1:, 1]).tolist(),
            s=100,
            c=[[0.2, 0.8, 0.2]],
        )

    ax.set_xlabel(x_label, size=15)
    ax.set_ylabel(y_label, size=15).set_rotation(0)
    ax.text(sc[0], sc[1], start_label)
    ax.text(tc[0], tc[1], target_label)
    ax.set_title(title)
    ax.axis("equal")
    plt.show()


def main(interactive=True, fw=None):
    global INTERACTIVE
    INTERACTIVE = interactive

    # Framework Setup #
    # ----------------#

    # choose random framework

    fw = aikit.choose_random_backend() if fw is None else fw
    aikit.set_backend(fw)

    # Spline Interpolation #
    # ---------------------#

    # config
    num_free_anchors = 3
    num_samples = 100
    constant_rot_vec = aikit.array([[0.0, 0.0, 0.0]])
    constant_z = aikit.array([[0.0]])

    # xy positions

    # 1 x 2
    start_xy = aikit.array([[0.0, 0.0]])
    target_xy = aikit.array([[1.0, 1.0]])

    # 1 x 2
    anchor1_xy = aikit.array([[0.6, 0.2]])
    anchor2_xy = aikit.array([[0.5, 0.5]])
    anchor3_xy = aikit.array([[0.4, 0.8]])

    # as 6DOF poses

    # 1 x 6
    start_pose = aikit.concat((start_xy, constant_z, constant_rot_vec), axis=-1)
    anchor1_pose = aikit.concat((anchor1_xy, constant_z, constant_rot_vec), axis=-1)
    anchor2_pose = aikit.concat((anchor2_xy, constant_z, constant_rot_vec), axis=-1)
    anchor3_pose = aikit.concat((anchor3_xy, constant_z, constant_rot_vec), axis=-1)
    target_pose = aikit.concat((target_xy, constant_z, constant_rot_vec), axis=-1)

    num_anchors = num_free_anchors + 2

    # num_anchors x 6
    anchor_poses = aikit.concat(
        (start_pose, anchor1_pose, anchor2_pose, anchor3_pose, target_pose), axis=0
    )

    # uniform sampling for spline

    # num_anchors x 1
    anchor_points = aikit.expand_dims(aikit.linspace(0.0, 1.0, num_anchors), axis=-1)

    # num_samples x 1
    query_points = aikit.expand_dims(aikit.linspace(0.0, 1.0, num_samples), axis=-1)

    # interpolated spline poses

    # num_samples x 6
    interpolated_poses = aikit_robot.sample_spline_path(
        anchor_points, anchor_poses, query_points
    )

    # xy motion

    # num_samples x 2
    anchor_xy_positions = anchor_poses[..., 0:2]

    # num_samples x 2
    interpolated_xy_positions = interpolated_poses[..., 0:2]

    # show xy path
    show_2d_spline_path(
        anchor_xy_positions,
        interpolated_xy_positions,
        [-0.095, 0.055],
        [0.638, 0.171],
        [0.544, 0.486],
        [0.445, 0.766],
        [0.9, 0.9],
        "x",
        "y",
        "Interpolated Drone Pose Spline in XY Plane",
        "start point",
        "target point",
    )

    # Rigid Mobile #
    # -------------#

    # drone relative body points
    rel_body_points = aikit.array(
        [
            [0.0, 0.0, 0.0],
            [-0.1, -0.1, 0.0],
            [-0.1, 0.1, 0.0],
            [0.1, -0.1, 0.0],
            [0.1, 0.1, 0.0],
        ]
    )

    # create drone as aikit rigid mobile robot
    drone = RigidMobile(rel_body_points)

    # rotatin vectors

    # 1 x 3
    start_rot_vec = aikit.array([[0.0, 0.0, 0.0]])
    target_rot_vec = aikit.array([[0.0, 0.0, np.pi]])

    # 1 x 3
    anchor1_rot_vec = aikit.array([[0.0, 0.0, np.pi / 4]])
    anchor2_rot_vec = aikit.array([[0.0, 0.0, 2 * np.pi / 4]])
    anchor3_rot_vec = aikit.array([[0.0, 0.0, 3 * np.pi / 4]])

    # as 6DOF poses

    # 1 x 6
    start_pose = aikit.concat((start_xy, constant_z, start_rot_vec), axis=-1)
    anchor1_pose = aikit.concat((anchor1_xy, constant_z, anchor1_rot_vec), axis=-1)
    anchor2_pose = aikit.concat((anchor2_xy, constant_z, anchor2_rot_vec), axis=-1)
    anchor3_pose = aikit.concat((anchor3_xy, constant_z, anchor3_rot_vec), axis=-1)
    target_pose = aikit.concat((target_xy, constant_z, target_rot_vec), axis=-1)

    # num_anchors x 6
    anchor_poses = aikit.concat(
        (start_pose, anchor1_pose, anchor2_pose, anchor3_pose, target_pose), axis=0
    )

    # interpolated spline poses

    # num_samples x 6
    interpolated_poses = aikit_robot.sample_spline_path(
        anchor_points, anchor_poses, query_points
    )

    # as matrices

    # num_anchors x 3 x 4
    anchor_matrices = aikit_mech.rot_vec_pose_to_mat_pose(anchor_poses)

    # num_samples x 3 x 4
    interpolated_matrices = aikit_mech.rot_vec_pose_to_mat_pose(interpolated_poses)

    # sample drone body

    # num_anchors x num_body_points x 3
    anchor_body_points = drone.sample_body(anchor_matrices)

    # num_samples x num_body_points x 3
    interpolated_body_points = drone.sample_body(interpolated_matrices)

    # show
    show_full_spline_path(
        anchor_body_points,
        interpolated_body_points,
        [-0.168, 0.19],
        [0.88, 0.73],
        "x",
        "y",
        "Sampled Drone Body Positions in XY Plane",
        "start points",
        "target points",
        False,
    )

    # Manipulator #
    # ------------#

    class SimpleManipulator(Manipulator):
        # noinspection PyShadowingNames
        def __init__(self, base_inv_ext_mat=None):
            a_s = aikit.array([0.5, 0.5])
            d_s = aikit.array([0.0, 0.0])
            alpha_s = aikit.array([0.0, 0.0])
            dh_joint_scales = aikit.ones((2,))
            dh_joint_offsets = aikit.array([-np.pi / 2, 0.0])
            super().__init__(
                a_s, d_s, alpha_s, dh_joint_scales, dh_joint_offsets, base_inv_ext_mat
            )

    # create manipulator as aikit manipulator
    manipulator = SimpleManipulator()

    # joint angles

    # 1 x 2
    start_joint_angles = aikit.array([[0.0, 0.0]])
    target_joint_angles = aikit.array([[-np.pi / 4, -np.pi / 4]])

    # 1 x 2
    anchor1_joint_angles = -aikit.array([[0.2, 0.6]]) * np.pi / 4
    anchor2_joint_angles = -aikit.array([[0.5, 0.5]]) * np.pi / 4
    anchor3_joint_angles = -aikit.array([[0.8, 0.4]]) * np.pi / 4

    # num_anchors x 2
    anchor_joint_angles = aikit.concat(
        (
            start_joint_angles,
            anchor1_joint_angles,
            anchor2_joint_angles,
            anchor3_joint_angles,
            target_joint_angles,
        ),
        axis=0,
    )

    # interpolated joint angles

    # num_anchors x 2
    interpolated_joint_angles = aikit_robot.sample_spline_path(
        anchor_points, anchor_joint_angles, query_points
    )

    # sample links

    # num_anchors x num_link_points x 3
    anchor_link_points = manipulator.sample_links(
        anchor_joint_angles, samples_per_metre=5
    )

    # num_anchors x num_link_points x 3
    interpolated_link_points = manipulator.sample_links(
        interpolated_joint_angles, samples_per_metre=5
    )

    # show
    show_2d_spline_path(
        anchor_joint_angles,
        interpolated_joint_angles,
        [-0.222, -0.015],
        [-0.147, -0.52],
        [-0.38, -0.366],
        [-0.64, -0.263],
        [-0.752, -0.79],
        r"$\theta_1$",
        r"$\theta_2$",
        "Interpolated Manipulator Joint Angles Spline",
        "start angles",
        "target angles",
    )
    show_full_spline_path(
        anchor_link_points,
        interpolated_link_points,
        [0.026, 0.8],
        [0.542, 0.26],
        "x",
        "y",
        "Sampled Manipulator Links in XY Plane",
        "start config",
        "target config",
        True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--non_interactive",
        action="store_true",
        help="whether to run the demo in non-interactive mode.",
    )
    parser.add_argument(
        "--backend",
        type=str,
        default=None,
        help="which backend to use. Chooses a random backend if unspecified.",
    )
    parsed_args = parser.parse_args()
    fw = parsed_args.backend
    main(not parsed_args.non_interactive, fw)
