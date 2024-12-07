# Use an official JMeter image as a base
FROM justb4/jmeter:latest

# Set the working directory inside the container
WORKDIR /jmeter

# Copy the JMeter test plan and required files into the container
COPY test-plan.jmx /jmeter/test-plan.jmx
COPY movie.csv /jmeter/movie.csv

# Create a directory for the results and reports
RUN mkdir -p /jmeter/results/report

# Run JMeter in non-GUI mode with the test plan
# Generate results and create an HTML report
ENTRYPOINT ["sh", "-c", "jmeter -n -t /jmeter/test-plan.jmx -l /jmeter/results/results.jtl && jmeter -g /jmeter/results/results.jtl -o /jmeter/results/report"]
