import math
from itertools import permutations
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.colors as mcolors

# Represents a box with dimensions, weight, category, and cost. It can be oriented in different ways.
class Box:
# Constructor method to initialize the object with its attributes.
    def __init__(self, box_id, length, width, height, weight,Category,Cost):
        self.x = None
        self.y = None
        self.z = None
        self.box_id = box_id
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.Category=Category
        self.Cost=Cost

# Calculates the volume of the object (Box or Space).
    def volume(self):
        return self.length * self.width * self.height
# Generates all possible orientations of a box based on its dimensions.

    def orientations(self):
        data =  list(permutations([self.length, self.width, self.height]))
        if(self.Category==1):
            sorted_data = sorted(data, key=lambda x: (-x[2],-x[0]))
        else:
            sorted_data=sorted(data, key=lambda x: (-x[0]^x[1]))
        return sorted_data


# Defines a free space in a bin for potential box placement. Includes dimensions and coordinates.
class Space:
# Constructor method to initialize the object with its attributes.
    def __init__(self, x, y, z, length, width, height):
        self.x = x
        self.y = y
        self.z = z
        self.length = length
        self.width = width
        self.height = height
# Calculates the volume of the object (Box or Space).

    def volume(self):
        return self.length * self.width * self.height

# Checks if a box can fit into the current space without exceeding bin constraints.
    def can_accommodate(self, box, bin):
        return self.length >= box.length and self.width >= box.width and self.height >= box.height and bin.weight >= box.weight + bin.current_weight
    def distance_to_corner(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

# Determines whether a box intersects with the current space.
    def intersects(self,box):
        return not (self.x + self.length <= box.x or
                    box.x + box.length <= self.x or
                    self.y + self.width <= box.y or
                    box.y + box.width <= self.y)

# Calculates the overlapping region between a box and a free space.
    def intersection(self,box):
        if not self.intersects(box):
            return None
        x1 = max(self.x, box.x)
        y1 = max(self.y, box.y)
        x2 = min(self.x + self.length, box.x + box.length)
        y2 = min(self.y + self.width, box.y + box.width)
        return (x1,y1,box.z,x2-x1,y2-y1,box.height)
# Represents a bin with specified dimensions and weight capacity for packing boxes.


class Bin:
# Constructor method to initialize the object with its attributes.
    def __init__(self, bin_id, length, width, height, weight):
        self.bin_id = bin_id
        self.length = length
        self.width = width
        self.height = height
        self.weight = weight
        self.current_weight = 0
        self.free_spaces = [Space(0, 0, 0, length, width, height)]
        self.packed_boxes = []
    def add_box(self, box, space):
        self.packed_boxes.append((box, space))
        self.split_spaces(box,space)
        self.prune_free_space()
# Calculates the volume of the object (Box or Space).

    def volume(self):
        return self.length*self.width*self.height

    def split_spaces(self,box,packed_space):
        new_spaces= []
        for free in self.free_spaces:
            if not free.intersects(box):
                new_spaces.append(free)
                continue
            intersection = free.intersection(box)
            if intersection is None:
                new_spaces.append(free)
                continue
            if intersection[1] > free.y:
                new_space = Space(free.x, free.y,free.z ,free.length, intersection[1] - free.y,free.height)
                new_spaces.append(new_space)
            if intersection[1] + intersection[4] < free.y + free.width:
                new_space = Space(
                    free.x,
                    intersection[1] + intersection[4],
                    free.z,
                    free.length,
                    free.y + free.width - (intersection[1] + intersection[4]),
                    free.height
                )
                new_spaces.append(new_space)
            if intersection[0] > free.x:
                new_space = Space(
                    free.x,
                    free.y,
                    free.z,
                    intersection[0] - free.x,
                    free.width,
                    free.height
                )
                new_spaces.append(new_space)
            if intersection[0] + intersection[3] < free.x + free.length:
                new_space = Space(
                    intersection[0] + intersection[3],
                    free.y,
                    free.z,
                    free.x + free.length - (intersection[0] + intersection[3]),
                    free.width,
                    free.height
                )
                new_spaces.append(new_space)
        if box.height < packed_space.height:
            new_spaces.append(Space(box.x,box.y,box.z+box.height,box.length,box.width,packed_space.height-box.height))
        self.free_spaces = new_spaces

# Removes redundant free spaces to optimize space management.
    def prune_free_space(self):
        pruned = []
        for i in range(len(self.free_spaces)):
            space1 = self.free_spaces[i]
            contained = False
            for j in range(len(self.free_spaces)):
                if i == j:
                    continue
                space2 = self.free_spaces[j]
                if (space1.x >= space2.x and
                    space1.y >= space2.y and
                    space1.x + space1.length <=space2.x +space2.length and
                    space1.y + space1.width <=space2.y +space2.width):
                    contained = True
                    break
            if not contained:
                pruned.append(space1)
        self.free_spaces = pruned

# Attempts to pack a box into the bin by finding a suitable free space.
    def pack_box(self, box):
        best_fit = sorted(self.free_spaces,key = lambda s : (s.volume() - box.volume(), s.distance_to_corner()))
        for chosen_space in best_fit:
            if chosen_space.can_accommodate(box,self):
                box.x = chosen_space.x
                box.y = chosen_space.y
                box.z = chosen_space.z
                self.add_box(box, chosen_space)
                self.current_weight += box.weight
                return True
        return False


# Defines sorting criteria for bins based on their volume, weight, and dimensions.
def bin_criteria(bins):
    vol = sorted(bins , key = lambda bin : (-bin.volume(),-bin.weight,-(bin.length*bin.width),-bin.height))
    return vol

# Defines sorting criteria for boxes based on priority, cost, and volume.
def box_criteria(boxes):
    vol = sorted(boxes, key=lambda box: (-box.Category,-box.Cost,-box.volume(),-box.weight, -(box.length * box.width)))
    return vol

def unpack_box_criteria(boxes):
    inc_vol1 = sorted(boxes, key=lambda box:
        ((max((box.height*box.length)/(box.width),
        (box.length*box.width)/(box.height))**1.47)
        *((((box.volume()**2.97)*(box.weight**0.755))))/(box.Cost**10)))
    return inc_vol1

# Calculates the total cost of packing, including penalties for unpacked priority boxes.
def cost(bins, k, boxes):
    priority_bins = 0
    total_cost = 0
    packed_ids = set()
    for bin in bins:
        priority = False
        for box, _ in bin.packed_boxes:
            packed_ids.add(box.box_id)
            if box.Category == 1 and not priority:
                priority = True
                priority_bins += 1
    for box in boxes:
        if box.box_id not in packed_ids:
            total_cost += box.Cost
    return k * priority_bins+total_cost, priority_bins

# Attempts to pack a box into the bin by finding a suitable free space.
def pack_boxes_into_multiple_bins(boxes_, bins_, k):
    min_unpacked = float('inf')  # Track minimum unpacked boxes
    best_solution = None
    bins_choice=bin_criteria(bins_)
    boxes_choice = box_criteria(boxes_)
    min_cost=float('inf')
    for num_bin_started in range(len(bins_)):
        for num_bin_ended in range(num_bin_started,len(bins_)):
            bins = bins_choice
            unpacked_boxes = []
            for bin in bins:
                bin.packed_boxes = []
                bin.free_spaces = [Space(0, 0, 0, bin.length, bin.width, bin.height)]
                bin.current_weight = 0  # Reset bin weight
            boxes=boxes_choice
            for box in boxes:
                packed = False
                orientations = box.orientations()
                for bin in bins:
                    for orientation in orientations:
                        box_orient = Box(box_id=box.box_id, length=orientation[0], width=orientation[1], height=orientation[2], weight=box.weight,Category=box.Category,Cost=box.Cost)
                        if bin.pack_box(box_orient):  # Removed extra `bin` parameter
                            packed = True
                            break
                    if packed:
                        break
                if not packed:
                    unpacked_boxes.append(box)
            unpacked_bins_hypo = bins[num_bin_started:num_bin_ended+1]
            unpacked_bins=[]
            for unpacked_bin in unpacked_bins_hypo:
                remove_bin_from_unpacked_bins=False
                for box,space in unpacked_bin.packed_boxes:
                    if(box.Category==1):
                        remove_bin_from_unpacked_bins=True
                        break
                if(remove_bin_from_unpacked_bins==False):
                    unpacked_bins.append(unpacked_bin)
            for bin in unpacked_bins:
                for box, _ in bin.packed_boxes:
                    unpacked_boxes.append(box)
                bin.packed_boxes = []
                bin.free_spaces = [Space(0, 0, 0, bin.length, bin.width, bin.height)]
                bin.current_weight = 0
            unpacked_boxes = unpack_box_criteria(unpacked_boxes)
            still_unpacked = []  # Track boxes that couldn't be packed in this phase
            for box in unpacked_boxes:
                packed = False
                orientations = box.orientations()
                orientations=orientations
                for bin in bins:  # Try packing into any bin, including previously emptied ones
                    for orientation in orientations:
                        box_orient = Box(box_id=box.box_id, length=orientation[0], width=orientation[1], height=orientation[2], weight=box.weight,Category=box.Category,Cost=box.Cost)
                        if bin.pack_box(box_orient):
                            packed = True
                            break
                    if packed:
                        break
                if not packed:
                    still_unpacked.append(box)  # Keep track of unpacked boxes
            unpacked_boxes = still_unpacked
            not_packed = len(unpacked_boxes)
            if cost(bins,k,boxes)[0]<min_cost:
                min_cost=cost(bins,k,boxes)[0]
                min_unpacked = not_packed
                best_solution = [Bin(bin.bin_id, bin.length, bin.width, bin.height, bin.weight) for bin in bins]
                for bin, best_bin in zip(bins, best_solution):
                    best_bin.packed_boxes = list(bin.packed_boxes)
                    best_bin.free_spaces = list(bin.free_spaces)
    return best_solution

# Validates the packing solution by checking for overlaps between boxes.
def check_overlaps(bins):
    """
    Check if any boxes in the bins overlap in the best solution.
    Args:
        bins (list): List of Bin objects containing packed boxes.
    Returns:
        bool: True if overlaps are found, False otherwise.
        list: List of overlapping pairs (box1_id, box2_id) if overlaps are found.
    """
    overlaps_found = False
    overlapping_pairs = []
    for bin in bins:
        # Get all packed boxes in the current bin
        packed_boxes = bin.packed_boxes
        num_boxes = len(packed_boxes)
        # Compare every pair of boxes in the bin
        for i in range(num_boxes):
            for j in range(i + 1, num_boxes):
                box1, space1 = packed_boxes[i]
                box2, space2 = packed_boxes[j]
                # Check overlap in all three dimensions
                overlap_x = not (space1.x + box1.length <= space2.x or space2.x + box2.length <= space1.x)
                overlap_y = not (space1.y + box1.width <= space2.y or space2.y + box2.width <= space1.y)
                overlap_z = not (space1.z + box1.height <= space2.z or space2.z + box2.height <= space1.z)
                # If there is an overlap in all three dimensions, they collide
                if overlap_x and overlap_y and overlap_z:
                    overlaps_found = True
                    overlapping_pairs.append((box1.box_id, box2.box_id))
    return overlaps_found, overlapping_pairs

# Example Usage:
# overlaps, overlapping_boxes = check_overlaps(best_solution)
# packed_box_ids = {box.box_id for bin in best_solution for box, _ in bin.packed_boxes}
# unpacked_boxes = [box for box in boxes if box.box_id not in packed_box_ids]
# c = 0
# if unpacked_boxes:
#     for box in unpacked_boxes:
#         c+=1

# Visualizes the packing of boxes within bins in a 3D representation.
def visualize_packing(bins):
    plt.style.use('dark_background')  # Set dark mode
    fig = plt.figure(figsize=(15, 10))
    num_bins = len(bins)
    for i, bin in enumerate(bins):
        ax = fig.add_subplot(2, (num_bins + 1) // 2, i + 1, projection='3d')
        ax.set_title(f'\n\nULD {bin.bin_id[1]}', color='white')
        ax.set_xlabel('Length', color='white')
        ax.set_ylabel('Width', color='white')
        ax.set_zlabel('Height', color='white')
        ax.set_xlim(0, bin.length)
        ax.set_ylim(0, bin.width)
        ax.set_zlim(0, bin.height)

        # Customizing axis and grid lines for dark mode
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.zaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='z', colors='white')
        ax.grid(color='gray', linestyle='--', linewidth=0.5)

        # Define vibrant colors for boxes
        colors = ['#402b90', '#f37a21']
        color_labels = ['Priority', 'Economy']  # Corresponding labels
        color_idx = 0

        for box, space in bin.packed_boxes:
            if box.Category == 1:
                color = colors[0]
            else:
                color = colors[1]
            x = [space.x, space.x + box.length, space.x + box.length, space.x, space.x, space.x + box.length, space.x + box.length, space.x]
            y = [space.y, space.y, space.y + box.width, space.y + box.width, space.y, space.y, space.y + box.width, space.y + box.width]
            z = [space.z, space.z, space.z, space.z, space.z + box.height, space.z + box.height, space.z + box.height, space.z + box.height]
            vertices = [
                [x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]], [x[3], y[3], z[3]],
                [x[4], y[4], z[4]], [x[5], y[5], z[5]], [x[6], y[6], z[6]], [x[7], y[7], z[7]]
            ]
            faces = [
                [vertices[j] for j in [0, 1, 5, 4]],  # Bottom face
                [vertices[j] for j in [2, 3, 7, 6]],  # Top face
                [vertices[j] for j in [0, 3, 7, 4]],  # Left face
                [vertices[j] for j in [1, 2, 6, 5]],  # Right face
                [vertices[j] for j in [0, 1, 2, 3]],  # Front face
                [vertices[j] for j in [4, 5, 6, 7]]   # Back face
            ]
            # Add 3D collection with distinct outlines
            ax.add_collection3d(Poly3DCollection(faces, facecolor=color, alpha=0.8, linewidths=1, edgecolors='white'))

        # Add legend to the subplot
        legend_elements = [
            plt.Line2D([0], [0], color=colors[0], lw=4, label=color_labels[0]),
            plt.Line2D([0], [0], color=colors[1], lw=4, label=color_labels[1])
        ]
        ax.legend(handles=legend_elements, loc='upper left', frameon=False, labelcolor='white')

        ax.view_init(elev=20, azim=30)

    plt.tight_layout()
    plt.show()
    # Generates a detailed summary of the packing results, including packed and unpacked boxes.
def get_result(best_solution, boxes, total_cost, unpacked_boxes, priority_bins):
    out = ""
    out+=f"{total_cost}, {len(boxes) - len(unpacked_boxes)}, {priority_bins} \n"
    for bin in best_solution:
        for box,_ in bin.packed_boxes:
            out+= (f"P-{box.box_id}, U{bin.bin_id}, {box.x}, {box.y}, {box.z}, {box.x + box.length}, {box.y + box.width}, {box.z + box.height} \n")
    for box in unpacked_boxes:
        out += (f"P-{box.box_id}, NONE, -1, -1, -1, -1, -1, -1 \n")
    return out

# out = get_result(best_solution, boxes, total_cost, unpacked_boxes, priority_bins)
# print(out)
# visualize_packing(best_solution)
# if overlaps:
#     print("Overlaps found between the following boxes:")
#     for box1, box2 in overlapping_boxes:
#         print(f"  Box {box1} overlaps with Box {box2}")
# else:
#     print("No overlaps found in the solution.")  
