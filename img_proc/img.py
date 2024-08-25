import cv2
import numpy as np
import os

# Function defined to find the centre of any contour then return its x and y coordinates as a tuple
def findCentre(contour):
    M = cv2.moments(contour)
    area = M['m00']
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return (cx, cy)

# Define paths
samples_folder = "samples/"
extracted_samples_folder = "extracted_samples/"
os.makedirs(extracted_samples_folder, exist_ok=True)
ideal_image_path = os.path.join(samples_folder, "ideal.jpg")

# Read the ideal image
ideal_image = cv2.imread(ideal_image_path)
ideal = cv2.cvtColor(ideal_image, cv2.COLOR_BGR2GRAY)

# Create thresholded binary mask of the ideal image
ret, ideal_threshold = cv2.threshold(ideal, 30, 255, cv2.THRESH_BINARY)

# Ideal diameter radius in pixels (assumed from comments)
ideal_radius = 25
ideal_area = np.pi * ideal_radius ** 2

def diameter_status(area):
    """Determine if the sample's inner diameter is larger, smaller, or the same compared to the ideal."""
    tolerance = 0.05  # 5% tolerance
    lower_limit = ideal_area * (1 - tolerance)
    upper_limit = ideal_area * (1 + tolerance)
    
    if area < lower_limit:
        return "Smaller"
    elif area > upper_limit:
        return "Larger"
    else:
        return "Same"

# Process each sample image
for idx, sample_image_name in enumerate(["sample2.jpg", "sample3.jpg", "sample4.jpg", "sample5.jpg", "sample6.jpg"], start=2):
    sample_image_path = os.path.join(samples_folder, sample_image_name)
    sample = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)

    # Create thresholded binary mask for the sample image
    ret, sample_threshold = cv2.threshold(sample, 30, 255, cv2.THRESH_BINARY)

    # Get the binary image of the ideal teeth
    ideal_teeth = cv2.cvtColor(ideal_image, cv2.COLOR_BGR2GRAY)
    cx, cy = findCentre(ideal_threshold)
    cv2.circle(ideal_teeth, (cx - 6, cy), 165, (0, 0, 0), -1)
    cv2.circle(ideal_teeth, (cx + 6, cy), 165, (0, 0, 0), -1)
    ret, ideal_teeth_threshold = cv2.threshold(ideal_teeth, 30, 255, cv2.THRESH_BINARY)
    ideal_teeth_erosion = cv2.erode(ideal_teeth_threshold, np.ones((3, 3), np.uint8), iterations=1)
    contours_ideal_teeth, _ = cv2.findContours(ideal_teeth_erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Find the difference between the ideal mask and the sample mask to get faulty parts
    difference = cv2.bitwise_xor(ideal_threshold, sample_threshold)
    cv2.circle(difference, (cx - 6, cy), 165, (0, 0, 0), -1)
    cv2.circle(difference, (cx + 6, cy), 165, (0, 0, 0), -1)
    difference_erosion = cv2.erode(difference, np.ones((3, 3), np.uint8), iterations=1)
    contours_difference, _ = cv2.findContours(difference_erosion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Draw bounding circles for each faulty tooth and match with ideal teeth
    contours_difference_centres = []
    for c in contours_difference:
        cx, cy = findCentre(c)
        cv2.circle(difference_erosion, (cx, cy), 22, (255, 255, 255), -1)
        contours_difference_centres.append((cx, cy))

    ideal_teeth_filtered = cv2.bitwise_and(difference_erosion, ideal_teeth_erosion)
    contours_ideal_teeth_filtered, _ = cv2.findContours(ideal_teeth_filtered, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    contours_ideal_teeth_filtered_centres = []
    for c in contours_ideal_teeth_filtered:
        cx, cy = findCentre(c)
        contours_ideal_teeth_filtered_centres.append((cx, cy))

    contours_ideal_teeth_matched = []
    count = 0
    for i in contours_difference_centres:
        diff_x, diff_y = i
        for j in contours_ideal_teeth_filtered_centres:
            ideal_x, ideal_y = j
            centre_distance = ((ideal_x - diff_x) ** 2 + (ideal_y - diff_y) ** 2) ** 0.5
            if centre_distance < 20:
                contours_ideal_teeth_matched.append(contours_ideal_teeth_filtered[count])
                break
            count += 1
        count = 0

    worn_out_teeth = 0
    broken_teeth = 0

    for i in range(len(contours_difference)):
        area_difference = cv2.contourArea(contours_difference[i])
        if i < len(contours_ideal_teeth_matched):
            area_ideal = cv2.contourArea(contours_ideal_teeth_matched[i])
            if area_difference / area_ideal < 0.85:
                worn_out_teeth += 1
            else:
                broken_teeth += 1

    # Inner diameter verification
    sample_diameter_path = os.path.join(samples_folder, sample_image_name)
    sample_image = cv2.imread(sample_diameter_path, cv2.IMREAD_GRAYSCALE)
    ideal_diameter = cv2.cvtColor(ideal_image, cv2.COLOR_BGR2GRAY)
    ret, ideal_diameter_threshold = cv2.threshold(ideal_diameter, 30, 255, cv2.THRESH_BINARY_INV)
    ret, sample_threshold = cv2.threshold(sample_image, 30, 255, cv2.THRESH_BINARY_INV)
    cv2.circle(ideal_diameter_threshold, (cx, cy), 300, (0, 0, 0), 500)
    cv2.circle(sample_threshold, (cx, cy), 300, (0, 0, 0), 500)
    contours_ideal_diameter, _ = cv2.findContours(ideal_diameter_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    contours_sample, _ = cv2.findContours(sample_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    diameter_status_text = ""
    if len(contours_sample) > 0:
        sample_area = cv2.contourArea(contours_sample[0])
        sample_radius = np.sqrt(sample_area / np.pi)
        sample_diameter = 2 * sample_radius
        status = diameter_status(sample_area)
        diameter_status_text = f"{sample_diameter:.2f} mm - {status} inner opening"
    else:
        diameter_status_text = "No inner diameter detected"

    # Generate description for the current sample
    description_parts = []
    if len(contours_difference) > 0:
        if broken_teeth > 0:
            description_parts.append(f"Broken teeth: {broken_teeth}")
        if worn_out_teeth > 0:
            description_parts.append(f"Worn out teeth: {worn_out_teeth}")

    description_parts.append(diameter_status_text)
    description = " + ".join(description_parts) if description_parts else "No defects detected"

    # Print results
    print(f"Sample {idx}: {description}")

    # Save the images
    result_image_path = os.path.join(extracted_samples_folder, f"defect_localization_{sample_image_name}")
    cv2.imwrite(result_image_path, difference_erosion)
