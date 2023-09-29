using System.Globalization;
using UnityEngine;

public class BlendshapesController : MonoBehaviour
{
    public SkinnedMeshRenderer skinnedMeshRenderer;
    public bool blinkBlendshape;

    public int leftEyeIndex;
    public int rightEyeIndex;
    public int blinkIndex;
    public int openMouthIndex;
    public int smileIndex;

    UdpSocket udpSocket;

    float leftEyeWeight;
    float rightEyeWeight;
    float openMouthWeight;
    float smileWeight;

    string[] weights;


    // Start is called before the first frame update
    void Start()
    {
        udpSocket = FindObjectOfType<UdpSocket>();
    }

    // Update is called once per frame
    void Update()
    {
        if (!string.IsNullOrEmpty(udpSocket.data))
        {
            weights = udpSocket.data.Split(',');
            leftEyeWeight = float.Parse(weights[0], CultureInfo.InvariantCulture);
            rightEyeWeight = float.Parse(weights[1], CultureInfo.InvariantCulture);
            openMouthWeight = float.Parse(weights[2], CultureInfo.InvariantCulture);
            smileWeight = float.Parse(weights[3], CultureInfo.InvariantCulture);

            if (blinkBlendshape)
            {
                skinnedMeshRenderer.SetBlendShapeWeight(blinkIndex, leftEyeWeight);
            }
            else
            {
                skinnedMeshRenderer.SetBlendShapeWeight(leftEyeIndex, leftEyeWeight);
                skinnedMeshRenderer.SetBlendShapeWeight(rightEyeIndex, rightEyeWeight);
            }
            skinnedMeshRenderer.SetBlendShapeWeight(openMouthIndex, openMouthWeight);
            skinnedMeshRenderer.SetBlendShapeWeight(smileIndex, smileWeight);
        }

        if (Input.GetKey("escape"))
        {
            Application.Quit();
        }
    }
}
