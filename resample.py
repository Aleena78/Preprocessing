#!/usr/bin/env python3
"""
Script to resample image through ITK.

Author: Leena Al-hazmi
"""

import os
import sys
import SimpleITK as sitk


def resample_image(input_path, output_path, upsample_factor=2.0):
    
    image = sitk.ReadImage(input_path)
    
    # Original spacing and size
    original_spacing = image.GetSpacing()  
    original_size = image.GetSize()        
    
    # Compute new spacing by dividing each by upsample_factor
    new_spacing = [sp / upsample_factor for sp in original_spacing]
    
    # Compute new size to maintain physical size
    new_size = [int(sz * upsample_factor) for sz in original_size]
    
    # resampler
    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetOutputSpacing(new_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(image.GetDirection())
    resampler.SetOutputOrigin(image.GetOrigin())
    resampler.SetOutputPixelType(image.GetPixelID())
    
    # Resample
    upsampled = resampler.Execute(image)
    
    # Write output
    sitk.WriteImage(upsampled, output_path)
    print(f"Upsampled image saved to {output_path}")


def main(tmp, anatfile, anatsuffix):
    # File paths
    echoavg_path = os.path.join(tmp, f"{anatfile}_echoavg_{anatsuffix}.nii.gz")
    optcom_path = os.path.join(tmp, f"{anatfile}_optcom_{anatsuffix}.nii.gz")
    t2star_path = os.path.join(tmp, f"{anatfile}_t2star_{anatsuffix}.nii.gz")

    echoavg_out = os.path.join(tmp, f"{anatfile}_echoavg_upsampled_{anatsuffix}.nii.gz")
    optcom_out = os.path.join(tmp, f"{anatfile}_optcom_upsampled_{anatsuffix}.nii.gz")
    t2star_out = os.path.join(tmp, f"{anatfile}_t2star_upsampled_{anatsuffix}.nii.gz")
    
    # Resample each image
    for in_path, out_path in [(echoavg_path, echoavg_out), (optcom_path, optcom_out), (t2star_path, t2star_out)]:
        if os.path.exists(in_path):
            resample_image(in_path, out_path)
        else:
            print(f"Warning: input file {in_path} does not exist. Skipping.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python resample_upsample.py <tmp> <anatfile> <anatsuffix>")
        sys.exit(1)
    tmp_dir = sys.argv[1]
    anat_file = sys.argv[2]
    anat_suffix = sys.argv[3]
    main(tmp_dir, anat_file, anat_suffix)
