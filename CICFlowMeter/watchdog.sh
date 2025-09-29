#!/bin/bash

exec 2>&1  # Redireciona stderr para stdout (log do container)

WATCH_DIR=${PCAPS_DIR:-/pcaps}
OUTPUT_DIR=${FLOWS_DIR:-/flows}
DELAY=${DELAY:-5}
CONVERT=${CONVERT_LINKTYPE:-0}

echo "[INFO] CICFlowMeter watcher started..."
echo "[INFO] PCAP directory: $WATCH_DIR"
echo "[INFO] Output directory: $OUTPUT_DIR"
echo "[INFO] Delay between checks: $DELAY seconds"
echo "[INFO] Convert to Ethernet: $CONVERT"

while true; do
  for file in "$WATCH_DIR"/*.pcap; do
    [ -e "$file" ] || continue

    filename=$(basename -- "$file")
    base="${filename%.*}"
    echo "[INFO] Processing $filename..."
    echo "[DEBUG] Checking file: $file"
    ls -lh "$file"

    # if [ "$CONVERT" = "1" ]; then
    #   converted="/tmp/${base}_ether.pcap"
    #   editcap -T ether "$file" "$converted"
    #   pcap_to_use="$converted"
    # else
    pcap_to_use="$file"
    # fi

    java -Djava.library.path=/app/lib/native \
      -cp "/app/CICFlowMeter-fat.jar:/app/lib/jnetpcap.jar" \
      cic.cs.unb.ca.ifm.Cmd \
      "$pcap_to_use" \
      "$OUTPUT_DIR"



    if [ $? -eq 0 ]; then
      # if [ "$CONVERT" = "1" ]; then
      #   csv_file="$OUTPUT_DIR/${base}_ether.pcap_Flow.csv"
      # else
      csv_file="$OUTPUT_DIR/${base}.pcap_Flow.csv"
      # fi

      echo "[INFO] Processed $filename, invoking producer on $csv_file..."
      # python3 /app/producer/producer.py "$csv_file" 2>&1
      PYTHONPATH=/app python3 -m producer.producer "$csv_file" 2>&1


      if [ $? -eq 0 ]; then
        echo "[INFO] Successfully processed $csv_file. Removing original PCAP."
        rm -f "$file"
        [ "$CONVERT" = "1" ] && rm -f "$converted"
      else
        echo "[WARN] Producer failed for $csv_file, will retry later."
      fi

    else
      echo "[WARN] CICFlowMeter failed to process $filename, will retry later."
    fi

  done

  sleep "$DELAY"
done
