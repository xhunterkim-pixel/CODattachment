using EFT.Interactive;
using UnityEditor;
using UnityEngine;

// Adds the left-hand grip poses from the vanilla Zenit RK-1 B-25U side grip to the selected prefab
// root, so the game uses the side-grip hand animation for it. Values are copied from
// foregrip_all_zenit_b25u_rk_1.bundle. Put this file in Assets/Editor/ of the SDK project.
public static class AddSideGripHandPoses
{
    [MenuItem("Tools/Add RK-1 B-25U Side Grip Hand Poses")]
    private static void Add()
    {
        var root = Selection.activeTransform;
        if (root == null)
        {
            EditorUtility.DisplayDialog("Side grip hand poses", "Select your grip's root object first.", "OK");
            return;
        }
        if (root.Find("Base HumanLPalm") != null)
        {
            EditorUtility.DisplayDialog("Side grip hand poses", "This object already has hand poses.", "OK");
            return;
        }

        Undo.SetCurrentGroupName("Add side grip hand poses");
        // Base HumanLPalm: GripType Alternative
        var palm0 = Bone(root, "Base HumanLPalm", new Vector3(0.15308693051338196f, 0.022915489971637726f, -0.0007072871667332947f), new Quaternion(0.6980247497558594f, 0.03378608450293541f, -0.21975761651992798f, 0.6806809902191162f));
        AddGripPose(palm0, (GripPose.EGripType)1);
        var palm0_0 = Bone(palm0, "Base HumanLDigit11", new Vector3(-0.041276682168245316f, -0.020866412669420242f, 0.04004118964076042f), new Quaternion(0.7904180884361267f, 0.3608839511871338f, 0.13730213046073914f, 0.47555243968963623f));
        var palm0_0_0 = Bone(palm0_0, "Base HumanLDigit12", new Vector3(-0.039770111441612244f, -2.2768973906295287E-07f, 5.7220457705398076E-08f), new Quaternion(-0.1591239720582962f, -0.02053328976035118f, 0.132130965590477f, 0.9781612157821655f));
        var palm0_0_0_0 = Bone(palm0_0_0, "Base HumanLDigit13 1", new Vector3(-0.03727259859442711f, 0.0f, -5.7220457705398076E-08f), new Quaternion(0.042291197925806046f, -0.0333842895925045f, 0.20646654069423676f, 0.9769690632820129f));
        var palm0_1 = Bone(palm0, "Base HumanLDigit21 1", new Vector3(-0.10533758997917175f, 0.0003160238265991211f, 0.03605392202734947f), new Quaternion(0.03051023930311203f, -0.1019100770354271f, 0.3914821743965149f, 0.9140160083770752f));
        var palm0_1_0 = Bone(palm0_1, "Base HumanLDigit22 1", new Vector3(-0.05621475726366043f, -7.390976008991856E-08f, 0.0f), new Quaternion(-0.038981229066848755f, -0.01623448356986046f, 0.5733470916748047f, 0.8182237148284912f));
        var palm0_1_0_0 = Bone(palm0_1_0, "Base HumanLDigit23 1", new Vector3(-0.027149813249707222f, 3.814697180359872E-08f, -1.5497207073167374E-07f), new Quaternion(0.00012847389734815806f, -0.0005782197113148868f, 0.33202117681503296f, 0.9432717561721802f));
        var palm0_2 = Bone(palm0, "Base HumanLDigit31 1", new Vector3(-0.10750260949134827f, 0.01188527513295412f, 0.008878707885742188f), new Quaternion(-0.023981187492609024f, -0.08764271438121796f, 0.48554012179374695f, 0.8694794178009033f));
        var palm0_2_0 = Bone(palm0_2, "Base HumanLDigit32 1", new Vector3(-0.05876743048429489f, -7.748603536583687E-08f, -1.5258788721439487E-07f), new Quaternion(-0.006580473855137825f, 0.013875065371394157f, 0.5249069929122925f, 0.8510210514068604f));
        var palm0_2_0_0 = Bone(palm0_2_0, "Base HumanLDigit33 1", new Vector3(-0.03349849581718445f, -1.19209286886246E-09f, 7.629394360719743E-08f), new Quaternion(-0.00024961214512586594f, -0.0005234323325566947f, 0.4847979247570038f, 0.8746260404586792f));
        var palm0_3 = Bone(palm0, "Base HumanLDigit41 1", new Vector3(-0.10514487326145172f, 0.009926867671310902f, -0.01626548171043396f), new Quaternion(-0.050601713359355927f, -0.08691804856061935f, 0.5538673996925354f, 0.826508104801178f));
        var palm0_3_0 = Bone(palm0_3, "Base HumanLDigit42 1", new Vector3(-0.050605762749910355f, -4.76837147544984E-09f, -3.0517577442878974E-07f), new Quaternion(-0.009216646663844585f, 0.03925858438014984f, 0.5069283246994019f, 0.8610444068908691f));
        var palm0_3_0_0 = Bone(palm0_3_0, "Base HumanLDigit43 1", new Vector3(-0.03003448247909546f, -7.390976008991856E-08f, -7.629394360719743E-08f), new Quaternion(-0.0003890645457431674f, -0.0004239392001181841f, 0.3852584660053253f, 0.9228085279464722f));
        var palm0_4 = Bone(palm0, "Base HumanLDigit51 1", new Vector3(-0.09869734197854996f, 0.002117414493113756f, -0.03863447904586792f), new Quaternion(-0.15355715155601501f, -0.11344977468252182f, 0.6285791397094727f, 0.7539480328559875f));
        var palm0_4_0 = Bone(palm0_4, "Base HumanLDigit52 1", new Vector3(-0.040162499994039536f, 2.3126601433887117E-07f, -3.814697180359872E-08f), new Quaternion(-0.0001843687641667202f, -0.00024739664513617754f, 0.4713785648345947f, 0.881930947303772f));
        var palm0_4_0_0 = Bone(palm0_4_0, "Base HumanLDigit53 1", new Vector3(-0.019784314557909966f, -7.629394360719743E-08f, -7.629394360719743E-08f), new Quaternion(-0.0003225627588108182f, 5.275369403534569E-05f, 0.31554901599884033f, 0.9489092230796814f));

        // Base HumanLPalm 1: GripType Common
        var palm1 = Bone(root, "Base HumanLPalm 1", new Vector3(0.08974526077508926f, 0.060844942927360535f, -0.10149502754211426f), new Quaternion(0.746475875377655f, 0.37191304564476013f, -0.5433655381202698f, 0.09595998376607895f));
        AddGripPose(palm1, (GripPose.EGripType)0);
        var palm1_0 = Bone(palm1, "Base HumanLDigit11 1", new Vector3(-0.04127662628889084f, -0.02086646668612957f, 0.04004119336605072f), new Quaternion(0.7389988303184509f, 0.36051145195961f, 0.12665970623493195f, 0.5548601150512695f));
        var palm1_0_0 = Bone(palm1_0, "Base HumanLDigit12 1", new Vector3(-0.03977014124393463f, -1.9073485191256623E-07f, -1.5258788721439487E-07f), new Quaternion(0.11988112330436707f, -0.0026955625507980585f, 0.2780364453792572f, 0.9530566930770874f));
        var palm1_0_0_0 = Bone(palm1_0_0, "Base HumanLDigit13", new Vector3(-0.03727264702320099f, 1.0281801188227746E-08f, 0.0f), new Quaternion(-0.04023528844118118f, -0.02003035694360733f, 0.375247061252594f, 0.9258345365524292f));
        var palm1_1 = Bone(palm1, "Base HumanLDigit21", new Vector3(-0.10533751547336578f, 0.0003160095075145364f, 0.036053918302059174f), new Quaternion(0.007779950276017189f, -0.1471996158361435f, 0.23770356178283691f, 0.9600878953933716f));
        var palm1_1_0 = Bone(palm1_1, "Base HumanLDigit22", new Vector3(-0.05621471256017685f, 2.38418573772492E-09f, -7.86781271244763E-08f), new Quaternion(-0.003551346017047763f, -0.025733429938554764f, 0.6342102289199829f, 0.7727241516113281f));
        var palm1_1_0_0 = Bone(palm1_1_0, "Base HumanLDigit23", new Vector3(-0.027149731293320656f, 7.629394360719743E-08f, -2.288818308215923E-07f), new Quaternion(0.00017246673814952374f, -0.0005590379587374628f, 0.41880637407302856f, 0.9080753922462463f));
        var palm1_2 = Bone(palm1, "Base HumanLDigit31", new Vector3(-0.10750259459018707f, 0.01188529934734106f, 0.008878779597580433f), new Quaternion(-0.02429543435573578f, -0.11980479955673218f, 0.4076964259147644f, 0.904897928237915f));
        var palm1_2_0 = Bone(palm1_2, "Base HumanLDigit32", new Vector3(-0.05876736342906952f, 1.573562542489526E-07f, -7.629394360719743E-08f), new Quaternion(0.00749595183879137f, -0.005883048288524151f, 0.5922985076904297f, 0.8056622743606567f));
        var palm1_2_0_0 = Bone(palm1_2_0, "Base HumanLDigit33", new Vector3(-0.03349853307008743f, -3.814697180359872E-08f, -7.629394360719743E-08f), new Quaternion(5.023266567150131E-05f, -0.0005782361258752644f, 0.4447470009326935f, 0.8956560492515564f));
        var palm1_3 = Bone(palm1, "Base HumanLDigit41", new Vector3(-0.10514478385448456f, 0.009926915168762207f, -0.01626540534198284f), new Quaternion(-0.03250536322593689f, -0.11358196288347244f, 0.4922187626361847f, 0.8624171018600464f));
        var palm1_3_0 = Bone(palm1_3, "Base HumanLDigit42", new Vector3(-0.050605740398168564f, -1.5139579545575543E-07f, -1.5258788721439487E-07f), new Quaternion(-0.024130506440997124f, 0.01290340069681406f, 0.5104324221611023f, 0.8594824075698853f));
        var palm1_3_0_0 = Bone(palm1_3_0, "Base HumanLDigit43", new Vector3(-0.030034484341740608f, -1.19209286886246E-09f, 0.0f), new Quaternion(-0.05928653106093407f, -0.011091588996350765f, 0.44342273473739624f, 0.8942809104919434f));
        var palm1_4 = Bone(palm1, "Base HumanLDigit51", new Vector3(-0.09869735687971115f, 0.00211738096550107f, -0.03863448649644852f), new Quaternion(-0.10010132938623428f, -0.11366014182567596f, 0.5555211305618286f, 0.817592442035675f));
        var palm1_4_0 = Bone(palm1_4, "Base HumanLDigit52", new Vector3(-0.04016254469752312f, 1.5139579545575543E-07f, -7.629394360719743E-08f), new Quaternion(-0.11172378808259964f, -0.06285662204027176f, 0.4917568564414978f, 0.8612444996833801f));
        var palm1_4_0_0 = Bone(palm1_4_0, "Base HumanLDigit53", new Vector3(-0.019784240052103996f, -4.0531158873591266E-08f, -1.5258788721439487E-07f), new Quaternion(-0.00030952011002227664f, -1.8932500097434968E-05f, 0.29712098836898804f, 0.954839825630188f));

        Debug.Log($"Added RK-1 B-25U side grip hand poses to {root.name}. Move the two 'Base HumanLPalm' objects so the palm sits on your grip, then apply the prefab.");
    }

    private static Transform Bone(Transform parent, string name, Vector3 localPosition, Quaternion localRotation)
    {
        var bone = new GameObject(name).transform;
        Undo.RegisterCreatedObjectUndo(bone.gameObject, "Add side grip hand poses");
        bone.SetParent(parent, false);
        bone.localPosition = localPosition;
        bone.localRotation = localRotation;
        return bone;
    }

    private static void AddGripPose(Transform palm, GripPose.EGripType gripType)
    {
        var pose = Undo.AddComponent<GripPose>(palm.gameObject);
        pose.DoorState = (EDoorState)7;
        pose.Hand = GripPose.EHand.Left;
        pose.GripType = gripType;
    }
}
