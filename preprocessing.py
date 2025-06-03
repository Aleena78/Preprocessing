import os
import re
import SimpleITK as sitk

bids_root = "/usr/share/Leena/M3PI/OrganizedData"
output_root = "/usr/share/Leena/M3PI/Sampled_averaged7T"
os.makedirs(output_root, exist_ok=True)

subject_ids = [f"sub-{str(i).zfill(2)}" for i in range(1, 7)]

for sub_id in subject_ids:
    anat_dir = os.path.join(bids_root, sub_id, "ses-7T", "anat")
    
    if not os.path.isdir(anat_dir):
        print(f"Anat directory not found for {sub_id} in ses-7T session.")
        continue

    output_anat_dir = os.path.join(output_root, sub_id, "ses-7T", "anat")
    os.makedirs(output_anat_dir, exist_ok=True)

    echo_images = []
    echo_filenames = []

    for file_name in os.listdir(anat_dir):
        if file_name.endswith(".nii") or file_name.endswith(".nii.gz"):
            input_path = os.path.join(anat_dir, file_name)
            image = sitk.ReadImage(input_path)
            echo_images.append(image)
            echo_filenames.append(file_name)

    if len(echo_images) == 0:
        print(f"No echo images found for {sub_id}")
        continue

    original_spacing = echo_images[0].GetSpacing()
    original_size = echo_images[0].GetSize()

    upsample_factor = 2.0

    new_spacing = [s / upsample_factor for s in original_spacing]
    new_size = [int(sz * upsample_factor) for sz in original_size]

    resampler = sitk.ResampleImageFilter()
    resampler.SetInterpolator(sitk.sitkLinear)  # Linear interpolation
    resampler.SetOutputSpacing(new_spacing)
    resampler.SetSize(new_size)
    resampler.SetOutputDirection(echo_images[0].GetDirection())
    resampler.SetOutputOrigin(echo_images[0].GetOrigin())

    # Upsample each echo image
    upsampled_images = [resampler.Execute(img) for img in echo_images]
 
    # Average the upsampled images
    if len(upsampled_images) > 1:
        average_image = sitk.Add(upsampled_images[0], upsampled_images[1])
        for img in upsampled_images[2:]:
            average_image = sitk.Add(average_image, img)
        average_image = sitk.Divide(average_image, len(upsampled_images))
    else:
        average_image = upsampled_images[0]

    # replace '_echo-<number>' with '_echo-average' for output
    first_filename = echo_filenames[0]
    if first_filename.endswith(".nii.gz"):
        base = first_filename[:-7]
        ext = ".nii.gz"
    elif first_filename.endswith(".nii"):
        base = first_filename[:-4]
        ext = ".nii"
    else:
        base = first_filename
        ext = ""

    base_no_echo = re.sub(r'_echo-\d+$', '', base)
    new_filename = base_no_echo + '_echo-average' + ext

    output_path = os.path.join(output_anat_dir, new_filename)
    sitk.WriteImage(average_image, output_path)
    print(f"Processed and saved averaged upsampled image: {output_path}")
