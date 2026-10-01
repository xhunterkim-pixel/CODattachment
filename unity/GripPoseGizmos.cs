using UnityEditor;
using UnityEngine;

// Draws every GripPose hand in the Scene view so you can line it up with the grip without
// building: a box for the palm, and joints and segments for each finger bone.
// Green = Common grip, orange = Alternative. Put this file in Assets/Editor/ of the SDK project.
public static class GripPoseGizmos
{
    // Rough hand size in metres, in the palm bone's local space: the fingers grow along -X.
    private static readonly Vector3 PalmCenter = new Vector3(-0.045f, 0f, 0f);
    private static readonly Vector3 PalmSize = new Vector3(0.09f, 0.025f, 0.085f);
    private const float JointSize = 0.006f;
    private const float FingertipLength = 0.02f;

    [DrawGizmo(GizmoType.Selected | GizmoType.NonSelected | GizmoType.Pickable)]
    private static void Draw(GripPose pose, GizmoType gizmoType)
    {
        var color = pose.GripType == GripPose.EGripType.Alternative
            ? new Color(1f, 0.55f, 0.1f)
            : new Color(0.3f, 1f, 0.3f);
        if ((gizmoType & GizmoType.Selected) == 0)
            color.a = 0.6f;
        Gizmos.color = color;

        var palm = pose.transform;
        var oldMatrix = Gizmos.matrix;
        Gizmos.matrix = palm.localToWorldMatrix;
        Gizmos.DrawWireCube(PalmCenter, PalmSize);
        Gizmos.matrix = oldMatrix;

        foreach (Transform finger in palm)
            DrawBone(palm, finger);
    }

    private static void DrawBone(Transform parent, Transform bone)
    {
        Gizmos.DrawLine(parent.position, bone.position);
        Gizmos.DrawSphere(bone.position, JointSize * 0.5f);
        if (bone.childCount == 0)
        {
            // Fingertip: the last bone has no child, so extend it a little along its own -X.
            Gizmos.DrawLine(bone.position, bone.position - bone.right * FingertipLength);
            return;
        }
        foreach (Transform child in bone)
            DrawBone(bone, child);
    }
}
