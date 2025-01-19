from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from optimiser import *
import time 

def pack(uld_filepath, boxes_filepath, write_filepath, k: int):
    print(k)
    
    boxes_df = pd.read_csv(boxes_filepath, header=None)
    bins_df = pd.read_csv(uld_filepath, header=None)

    Priority=1
    Economy=0

    boxes = [ Box(
        box_id=str(row[0]), 
        length=int(row[1]), 
        width=int(row[2]), 
        height=int(row[3]), 
        weight=int(row[4]), 
        Category = Economy if (str(row[5]).lower() == 'economy') else Priority, 
        Cost = int(row[6]) if (str(row[6]) != '-') else 0
    ) for _, row in boxes_df.iterrows() ]

    boxes_priority=[]
    boxes_economy=[]
    for i in range(len(boxes)):
        if(boxes[i].Category==Priority):
            boxes_priority.append(boxes[i])
        else:
            boxes_economy.append(boxes[i])
    
    bins = [Bin(
        str(row[0]),
        int(row[1]),
        int(row[2]),
        int(row[3]),
        int(row[4])
    ) for _,row in bins_df.iterrows()]

    best_solution = pack_boxes_into_multiple_bins(boxes, bins, k)
    packed_box_ids = [box.box_id for bin in best_solution for box, _ in bin.packed_boxes]
    unpacked_boxes = [box for box in boxes if box.box_id not in packed_box_ids]

    priority_bins = 0  
    total_cost = 0  
    for bin in best_solution:
        priority = False
        for box, _ in bin.packed_boxes: 
            if box.Category == 1 and not priority:
                priority = True
                priority_bins += 1
                break
    for box in unpacked_boxes:
        total_cost += box.Cost
    total_cost += k * priority_bins

    with open(write_filepath, 'wt') as file:
        file.write(f'{total_cost},{len(packed_box_ids)},{priority_bins}\n')

        for bin in best_solution:
            for box, space in bin.packed_boxes:
                file.write(f'{box.box_id},{bin.bin_id},{space.x},{space.y},{space.z},{space.x+box.length},{space.y+box.width},{space.z+box.height}\n')
        
        for box in unpacked_boxes:
            file.write(f'{box.box_id},NONE,-1,-1,-1,-1,-1,-1\n')
    
    return best_solution
    # Display results
    # for bin in best_solution:
    #     print(f"\nBin {bin.bin_id}: Dimensions ({bin.length}x{bin.width}x{bin.height})")
    #     print("  Packed Boxes:")
    #     for box, space in bin.packed_boxes:
    #         print(f"    Box {box.box_id} packed at position ({space.x}, {space.y}, {space.z}) with dimensions {box.length}x{box.width}x{box.height}")
        
    #     print(f"  Free Spaces ({len(bin.free_spaces)} total):")
    #     for space in bin.free_spaces:
    #         print(f"    Space at ({space.x}, {space.y}, {space.z}) with dimensions ({space.length}x{space.width}x{space.height})")

app = Flask(__name__)
app.config['ULD_UPLOAD'] = 'uploads/uld/'
app.config['BOXES_UPLOAD'] = 'uploads/boxes/'
app.config['OUTPUT'] = 'outputs/'

@app.route('/')
def home():
    return render_template('index.html')

@app.get('/upload')
def upload_file():
    return render_template('upload.html')

upload_counter = 0
@app.post('/upload')
def process_file():
    global upload_counter

    if (request.files['uld_file'] and request.files['boxes_file']):
        upload_counter += 1

        uld_path = os.path.join(app.config['ULD_UPLOAD'], f'upload_{upload_counter}.csv')
        request.files['uld_file'].save(uld_path)

        boxes_path = os.path.join(app.config['BOXES_UPLOAD'], f'upload_{upload_counter}.csv')
        request.files['boxes_file'].save(boxes_path)

        write_path = os.path.join(app.config['OUTPUT'], f'output_{upload_counter}.txt')
        start = time.time()
        best_solution = pack(uld_path, boxes_path, write_path, int(request.form['k']))
        visualize_packing(best_solution)
        end = time.time()
        print(end - start)
        return send_file(write_path, as_attachment=True)
    

if (__name__ == '__main__'):
    app.run(debug=True)