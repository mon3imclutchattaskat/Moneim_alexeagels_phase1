import cv2
import numpy as np
import os

def calculate_diameter(contour):
    """Calculate the diameter of the gear based on its contour."""
    # Fit a minimum enclosing circle to the contour
    (x, y), radius = cv2.minEnclosingCircle(contour)
    diameter = 2 * radius
    return diameter

def detect_defects_and_diameter(ideal_image_path, samples_folder_path):
    # Check if the ideal image file exists
    if not os.path.isfile(ideal_image_path):
        print(f"Error: The ideal image file '{ideal_image_path}' does not exist.")
        return

    # Load the ideal gear image
    ideal_image = cv2.imread(ideal_image_path, cv2.IMREAD_GRAYSCALE)
    
    # Check if the image was loaded successfully
    if ideal_image is None:
        print(f"Error: Could not open or read the image '{ideal_image_path}'.")
        return
    
    # Apply Gaussian Blur to the ideal image for smoothing
    ideal_blur = cv2.GaussianBlur(ideal_image, (5, 5), 0)
    
    # Perform edge detection on the ideal image
    ideal_edges = cv2.Canny(ideal_blur, 50, 150)
    
    # Find contours in the ideal image
    ideal_contours, _ = cv2.findContours(ideal_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Calculate the diameter of the ideal gear
    ideal_diameter = max(calculate_diameter(contour) for contour in ideal_contours if cv2.contourArea(contour) > 1000)
    
    # List all sample images in the folder
    sample_image_paths = [os.path.join(samples_folder_path, f) for f in os.listdir(samples_folder_path) if f.endswith('.jpg') or f.endswith('.png')]
    
    for sample_image_path in sample_image_paths:
        # Load the sample gear image
        sample_image = cv2.imread(sample_image_path, cv2.IMREAD_GRAYSCALE)
        
        # Check if the image was loaded successfully
        if sample_image is None:
            print(f"Error: Could not open or read the image '{sample_image_path}'.")
            continue
        
        # Apply Gaussian Blur to the sample image
        sample_blur = cv2.GaussianBlur(sample_image, (5, 5), 0)
        
        # Perform edge detection on the sample image
        sample_edges = cv2.Canny(sample_blur, 50, 150)
        
        # Find contours in the sample image
        sample_contours, _ = cv2.findContours(sample_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate the diameter of the sample gear
        sample_diameter = max(calculate_diameter(contour) for contour in sample_contours if cv2.contourArea(contour) > 1000)
        
        # Find the difference between the ideal and sample edges
        diff_edges = cv2.bitwise_xor(ideal_edges, sample_edges)

        # Find contours in the difference image
        diff_contours, _ = cv2.findContours(diff_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area to distinguish between broken and worn teeth
        broken_teeth_count = 0
        worn_teeth_count = 0

        for contour in diff_contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # You can adjust this threshold based on your image
                broken_teeth_count += 1
            else:
                worn_teeth_count += 1

        # Determine diameter difference
        if abs(sample_diameter - ideal_diameter) < 10:  # Threshold for diameter similarity
            diameter_status = "identical"
        elif sample_diameter > ideal_diameter:
            diameter_status = "larger"
        else:
            diameter_status = "smaller"

        # Print the result
        print(f"Results for {os.path.basename(sample_image_path)}:")
        print(f"  Diameter Status: {diameter_status}")
        print(f"  Broken Teeth Count: {broken_teeth_count}")
        print(f"  Worn Teeth Count: {worn_teeth_count}")

# Define paths to the ideal image and samples folder
ideal_image_path = 'samples/ideal.jpg'
samples_folder_path = 'samples'

# Run the defect detection and diameter comparison
detect_defects_and_diameter(ideal_image_path, samples_folder_path)

