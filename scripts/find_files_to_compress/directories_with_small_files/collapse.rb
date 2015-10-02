### Written by IsmailM
## Description
#   Collapse the find results into fewer entries
## Usage:
# ruby collapse.rb INPUT_LOG_FILE

def read_input_data(s)
  input_data = {}
  s.each_line do |l|
    l.scan(/(\d+)\s+(\S+)/) do |n, path|
      parent = File.dirname(path)
      input_data[parent] ||= []
      input_data[parent] << { number: n.to_i, path: path }
    end
  end
  input_data
end

def collapse_into_parent(input)
  data = {}
  input.each do |path, array|
    next if array.length < 5
    parent = File.dirname(path)
    data[parent] ||= []
    total_number_of_files = array.map { |h| h[:number] }.reduce(:+)
    data[parent] << { number: total_number_of_files.to_i, path: path }
  end
  data
end

def print_output(data)
  data.each { |_, a| a.each { |h| puts format_results(h) } }
end

def format_results(h)
  format("%10s\t%s", h[:number], h[:path])
end

content = IO.read(ARGV[0])
data = read_input_data(content)
data = collapse_into_parent(data) while data.values.map(&:length).max > 30
print_output(data)
