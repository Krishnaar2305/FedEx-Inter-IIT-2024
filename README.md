
# Packing Optimization Algorithm

This project provides a Python implementation for optimizing 3D bin packing. The algorithm efficiently arranges boxes into bins while respecting constraints such as dimensions, weight, priority levels, and cost.

---

## Key Features

1. **Flexible Box Orientations**: Automatically determines the best orientations for boxes to maximize packing efficiency.
2. **Priority-based Packing**: Handles `Priority` and `Economy` categories with special care for priority items.
3. **Cost Optimization**: Minimizes the total packing cost by prioritizing efficient space utilization.
4. **Dynamic Space Management**: Continuously updates available spaces within bins during packing.
5. **Validation**: Ensures no overlaps between packed boxes.
6. **Visualization**: Provides 3D visualizations of packed bins for better insights.

---

## Input and Output Formats

### Input Files

The input files must include:

- **Bin Details File**:  
  ```plaintext
  U<ID>,<length>,<width>,<height>,<weight>
  ```  
  Example:  
  ```plaintext
  U1,120,80,100,500
  U2,100,100,100,300
  ```

- **Box Details File**:  
  ```plaintext
  P-<ID>,<length>,<width>,<height>,<weight>,<Priority/Economy>,<Cost>
  ```  
  Example:  
  ```plaintext
  P-1,50,40,30,10,Priority,-
  P-2,30,30,30,5,Economy,200
  ```

### Output File

- **Summary**:  
  ```plaintext
  <total_cost>,<number_of_packed_boxes>,<number_of_priority_bins>
  ```

- **Packed Boxes**:  
  ```plaintext
  P-<box_id>,U<bin_id>,<x_start>,<y_start>,<z_start>,<x_end>,<y_end>,<z_end>
  ```

- **Unpacked Boxes**:  
  ```plaintext
  P-<box_id>,NONE,-1,-1,-1,-1,-1,-1
  ```

---

## How to Use

### Prerequisites

1. Install Python 3.x on your system.
2. Install the required libraries using pip:  
   ```bash
   pip install matplotlib flask
   ```

### Running the Program

1. Prepare your input file (e.g., `Challenge_FedEx.txt`) in the correct format.
2. Update the `file_path_ULD` and `file_path_boxes` variables in the script to the path of your input files.
3. Execute the script:  
   ```bash
   python app.py
   ```
4. A server will start on http://127.0.0.1:5000 where you can upload the files
5. Enter the value of K, the cost for each ULD with priority package, on prompt.
6. The results will be saved in `output.txt` and a 3D visualization will be displayed.

---

## Example

### Input Files

#### ULD File (`ULD_WH.txt`)
```plaintext
U1,120,80,100,500
U2,100,100,100,300
```

#### Boxes File (`Boxes_WH.txt`)
```plaintext
P-1,50,40,30,10,Priority,500
P-2,30,30,30,5,Economy,200
P-3,60,60,40,20,Priority,300
```

### Output File (`output.txt`)

```plaintext
800,2,1
P-1,U1,0,0,0,50,40,30
P-3,U2,0,0,0,60,60,40
P-2,NONE,-1,-1,-1,-1,-1,-1
```

### Visualization

The script generates a 3D plot of the packing solution, illustrating how boxes are arranged within each bin.

---

## Functionality Overview

### Main Functions

1. **`pack_boxes_into_multiple_bins(boxes, bins, k)`**:  
   Optimizes the packing of boxes into bins while minimizing costs and unpacked items.

2. **`visualize_packing(bins)`**:  
   Produces a 3D visualization of the packed bins.

3. **`check_overlaps(bins)`**:  
   Verifies if any boxes overlap within the packed bins.

4. **`cost(bins, k)`**:  
   Calculates the total cost of packing, including penalties for unpacked priority boxes.

5. **`parse_input(file_path)`**:  
   Parses input files to extract bin and box information.

### Classes

1. **`Box`**: Represents a box with dimensions, weight, priority, and cost.
2. **`Space`**: Defines a free space within a bin.
3. **`Bin`**: Represents a ULD bin with dimensions, weight capacity, and packed boxes.

---

## Notes

- Ensure input files strictly follow the specified format to avoid parsing errors.
- Use the cost multiplier (`K`) to balance priorities and penalties effectively.

