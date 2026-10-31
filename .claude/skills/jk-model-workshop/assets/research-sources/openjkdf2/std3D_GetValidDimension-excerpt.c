void std3D_GetValidDimension(unsigned int inW, unsigned int inH, unsigned int *outW, unsigned int *outH)
{
    // TODO hack for JKE? I don't know what they're doing
    *outW = inW > 256 ? 256 : inW;
    *outH = inH > 256 ? 256 : inH;
}
