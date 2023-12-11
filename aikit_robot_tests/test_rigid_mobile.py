"""
Collection of tests for mico robot manipulator
"""

# global
import aikit
import aikit_mech
import numpy as np

# local
from aikit_robot.rigid_mobile import RigidMobile


class RigidMobileTestData:
    def __init__(self):
        rot_vec_pose = aikit.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
        self.inv_ext_mat = aikit_mech.rot_vec_pose_to_mat_pose(rot_vec_pose)
        self.rel_body_points = aikit.array(
            [
                [0.0, 0.0, 0.0],
                [-0.2, -0.2, 0.0],
                [-0.2, 0.2, 0.0],
                [0.2, -0.2, 0.0],
                [0.2, 0.2, 0.0],
            ]
        )
        self.sampled_body = aikit.array(
            [
                [0.1, 0.2, 0.3],
                [0.04361792, -0.0751835, 0.26690764],
                [-0.12924806, 0.22732089, 0.46339797],
                [0.32924806, 0.17267911, 0.13660203],
                [0.15638208, 0.4751835, 0.33309236],
            ]
        )


def test_sample_body(device, fw):
    aikit.set_backend(fw)
    td = RigidMobileTestData()
    mico = RigidMobile(aikit.array(td.rel_body_points, dtype="float32"))
    assert np.allclose(mico.sample_body(td.inv_ext_mat), td.sampled_body, atol=1e-6)
    assert np.allclose(
        mico.sample_body(np.tile(np.expand_dims(td.inv_ext_mat, 0), (5, 1, 1))),
        np.tile(np.expand_dims(td.sampled_body, 0), (5, 1, 1)),
        atol=1e-6,
    )
    aikit.previous_backend()
