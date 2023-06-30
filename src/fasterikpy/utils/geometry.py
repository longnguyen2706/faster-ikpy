# coding= utf8
"""
.. module:: geometry_utils
This module contains helper functions used to compute 3D geometric transformations.
"""
import jax.numpy as jnp
import sympy


def rx_matrix(theta):
    """Rotation matrix around the X axis"""
    return jnp.array([
        [1, 0, 0],
        [0, jnp.cos(theta), -jnp.sin(theta)],
        [0, jnp.sin(theta), jnp.cos(theta)]
    ])


def rz_matrix(theta):
    """Rotation matrix around the Z axis"""
    return jnp.array([
        [jnp.cos(theta), -jnp.sin(theta), 0],
        [jnp.sin(theta), jnp.cos(theta), 0],
        [0, 0, 1]
    ])


def symbolic_rz_matrix(symbolic_theta):
    """Matrice symbolique de rotation autour de l'axe Z"""
    return sympy.Matrix([
        [sympy.cos(symbolic_theta), -sympy.sin(symbolic_theta), 0],
        [sympy.sin(symbolic_theta), sympy.cos(symbolic_theta), 0],
        [0, 0, 1]
    ])


def ry_matrix(theta):
    """Rotation matrix around the Y axis"""
    return jnp.array([
        [jnp.cos(theta), 0, jnp.sin(theta)],
        [0, 1, 0],
        [-jnp.sin(theta), 0, jnp.cos(theta)]
    ])


def rotation_matrix(phi, theta, psi):
    """Return a rotation matrix using the given Euler angles"""
    return jnp.dot(rz_matrix(phi), jnp.dot(rx_matrix(theta), rz_matrix(psi)))


def symbolic_rotation_matrix(phi, theta, symbolic_psi):
    """Retourne une matrice de rotation où psi est symbolique"""
    return sympy.Matrix(rz_matrix(phi)) * sympy.Matrix(rx_matrix(theta)) * symbolic_rz_matrix(symbolic_psi)


def rpy_matrix(roll, pitch, yaw):
    """Return a rotation matrix described by the extrinsinc roll, pitch, yaw coordinates"""
    return jnp.dot(rz_matrix(yaw), jnp.dot(ry_matrix(pitch), rx_matrix(roll)))


def _axis_rotation_matrix_formula(x, y, z, c, s):
    return jnp.array([
        [x ** 2 + (1 - x ** 2) * c, x * y * (1 - c) - z * s, x * z * (1 - c) + y * s],
        [x * y * (1 - c) + z * s, y ** 2 + (1 - y ** 2) * c, y * z * (1 - c) - x * s],
        [x * z * (1 - c) - y * s, y * z * (1 - c) + x * s, z ** 2 + (1 - z ** 2) * c]
    ])


def axis_rotation_matrix(axis, theta):
    """Returns a rotation matrix around the given axis"""
    [x, y, z] = axis
    c = jnp.cos(theta)
    s = jnp.sin(theta)
    return jnp.array(_axis_rotation_matrix_formula(x, y, z, c, s))


def symbolic_axis_rotation_matrix(axis, symbolic_theta):
    """Returns a rotation matrix around the given axis"""
    [x, y, z] = axis
    c = sympy.cos(symbolic_theta)
    s = sympy.sin(symbolic_theta)
    return sympy.Matrix(_axis_rotation_matrix_formula(x, y, z, c, s))


def get_translation_matrix(mu):
    """Returns a translation matrix of the given mu"""
    translation_matrix = jnp.eye(4)
    translation_matrix.at[:3, 3].set(mu)
    return translation_matrix


def get_symbolic_translation_matrix(mu):
    """Returns a translation matrix of the given mu"""
    translation_matrix = sympy.eye(4)
    translation_matrix[:3, 3] = mu
    return sympy.Matrix(translation_matrix)


def homogeneous_translation_matrix(trans_x, trans_y, trans_z):
    """Return a translation matrix the homogeneous space"""
    return jnp.array([jnp.array([1, 0, 0, trans_x]), jnp.array([0, 1, 0, trans_y]), jnp.array([0, 0, 1, trans_z]), jnp.array([0, 0, 0, 1])])


def from_transformation_matrix(transformation_matrix):
    """Convert a transformation matrix to a tuple (translation_vector, rotation_matrix)"""
    return transformation_matrix[:, -1], transformation_matrix[:-1, :-1]


def to_transformation_matrix(translation, orientation_matrix=jnp.zeros((3, 3))):
    """Convert a tuple (translation_vector, orientation_matrix) to a transformation matrix

    Parameters
    ----------
    translation: numpy.array
        The translation of your frame presented as a 3D vector.
    orientation_matrix: numpy.array
        Optional : The orientation of your frame, presented as a 3x3 matrix.
    """
    matrix = jnp.eye(4)
    matrix.at[:-1, :-1].set(orientation_matrix)
    matrix.at[:-1, -1].set(translation)
    return matrix


def cartesian_to_homogeneous(cartesian_matrix, matrix_type="numpy"):
    """Converts a cartesian matrix to an homogeneous matrix"""
    dimension_x, dimension_y = cartesian_matrix.shape
    # Square matrix
    # Manage different types fo input matrixes
    if matrix_type == "numpy":
        homogeneous_matrix = jnp.eye(dimension_x + 1)
    elif matrix_type == "sympy":
        homogeneous_matrix = sympy.eye(dimension_x + 1)
    else:
        raise ValueError("Unknown matrix_type: {}".format(matrix_type))
    # Add a column filled with 0 and finishing with 1 to the cartesian matrix to transform it into an homogeneous one
    homogeneous_matrix.at[:-1, :-1].set(cartesian_matrix)

    return homogeneous_matrix


def cartesian_to_homogeneous_vectors(cartesian_vector, matrix_type="numpy"):
    """Converts a cartesian vector to an homogeneous vector"""
    dimension_x = cartesian_vector.shape[0]
    # Vector
    if matrix_type == "numpy":
        homogeneous_vector = jnp.zeros(dimension_x + 1)
        # Last item is a 1
        homogeneous_vector.at[-1].set(1)
        homogeneous_vector.at[:-1].set(cartesian_vector)
    else:
        raise ValueError("Unknown matrix_type: {}".format(matrix_type))
    return homogeneous_vector


def homogeneous_to_cartesian_vectors(homogeneous_vector):
    """Convert an homogeneous vector to cartesian vector"""""
    return homogeneous_vector[:-1]


def homogeneous_to_cartesian(homogeneous_matrix):
    """Convert an homogeneous matrix to cartesian matrix"""
    return homogeneous_matrix[:-1, :-1]
