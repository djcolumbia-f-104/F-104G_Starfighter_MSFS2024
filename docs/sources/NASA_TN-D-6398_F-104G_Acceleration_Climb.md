| NASA TECHNICAL  |     |     | NOTE  |     |
| --------------- | --- | --- | ----- | --- |
FLIGHT-DETERMINED ACCELERATION

| AND CLIMB  |           | PERFORMANCE  |      | OF
  |
| ---------- | --------- | ------------ | ---- | ----- |
| AN F-lO4G  | AIRPLANE  |              | FOR  | USE
 |
IN AN OPTIMUM-FLIGHT-PATH

| COMPUTER          | PROGRAM
    |         |     |     |
| ----------------- | ------------ | ------- | --- | --- |
| by  Robert        | T. Marshull  |         |     |     |
| Flight  Reseurch  |              | Center  |     |     |
| Edwurds,          | CuZ$         | 93523   |     |     |
NATIONAL  AERONAUTICS  AND  SPACE  ADMINISTRATION  WASHINGTON,  D.  C.  JUNE  1971

TECH LIBRARY KAFB,NM
lllllllIlllll III I I1ll I1ll

0332924

| - _  _ | _ ­ |     |     |     |     |     |
| ------ | --- | --- | --- | --- | --- | --- |
1. Report No.  2. Government Accession No.  3. Recipient's  Catalog No.
NASA TN D-6398
--.
| 4.  Title and Subtitle  |     |     |     |     | 5. 	 Report Date  |     |
| ----------------------- | --- | --- | --- | --- | ----------------- | --- |
FLIGHT-DETERMINED ACCELERATION AND CLIMB PERFORMANCE OF  June 19n
AN F-104G AIRPLANE FOR USE IN AN OPTIMUM-FLIGHT-PATH
6. Performing Organization Code
COMPUTER PROGRAM
~.
7. Author(s)
| Robert T.  | Marshall  |     |     |     |     |     |
| ---------- | --------- | --- | --- | --- | --- | --- |
.. . ­
9.  Performing Organization Name and Address
NASA Flight Research Center

P. 0. Box 273

| Edwards, California  |     | 93523
 |     |     |     |     |
| -------------------- | --- | ------- | --- | --- | --- | --- |
2. Sponsoring Agency Name and Address
|     |     |     |     |     | .~  Techniga!  Note-­ |     |
| --- | --- | --- | --- | --- | --------------------- | --- |
National Aeronautics and Space Administration
14. Sponsoring Agency Code
| Washington, D.  | C.  | 20546  |     |     |     |     |
| --------------- | --- | ------ | --- | --- | --- | --- |
I
._
5. Supplementary Notes
|     | ~.  | ..  - |     | ~  ~  | .   |     |
| --- | --- | ----- | --- | ----- | --- | --- |
6. Abstract
A flight-test investigation was conducted to determine the
standard-day performance characteristics (excess thrust, fuel flow,
and climb potential) at maximum afterburner power for an F-104G
|     |     | airplane.  The tests were conducted at Mach numbers from 0.5 to  |     |     |     |     |
| --- | --- | ---------------------------------------------------------------- | --- | --- | --- | --- |
2. 0 and at altitudes from 5000 feet (1524 meters) to 50,000 feet
(15,240 meters).
The standard-day excess thrust and fuel-flow data obtained
from the investigation were used to define a computer model of
|     | the performance of the test airplane.  |     | In addition, the climb-potential  |     |     |     |
| --- | -------------------------------------- | --- | --------------------------------- | --- | --- | --- |
(specific excess power) data obtained from the flight tests were
|     |     | compared with the available predicted climb-potential data.  |     |     | From  |     |
| --- | --- | ------------------------------------------------------------ | --- | --- | ----- | --- |
the comparisons, it was found that the predicted data for the "average"
I.'-104G airplane did not represent the performance of the test air­
plane as accurately as required for the computation of meaningful
Therefore, to compute meaningful flight
flight trajectories.
trajectories for the test airplane, the flight-derived model should
be used
| _ _   |     | -   |     | ~   | . .  ..  |     |
| ----- | --- | --- | --- | --- | -------- | --- |
7.  Key Words (Suggested by Author(s) )  18. Distribution Statement
| Performance  |     |     |     | Unclassified -Unlimited
 |     |     |
| ------------ | --- | --- | --- | ------------------------- | --- | --- |
F-104G airplane

Trajectory optimization

I  I
19. Security Classif. (of this report)  20. Security Classif. (of this page)  21. NO.  of Pages
I  I
| Unclassified  |     |     | Unclassified  |     |     | $3.00  |
| ------------- | --- | --- | ------------- | --- | --- | ------ |
-
For sale by the National Technical Information Service, Springfield, Virginia 22151

FLIGHT-DETERMINED ACCELERATION AND CLIMB PERFORMANCE
OF AN F-104G AIRPLANE FOR USE IN AN OPTIMUM-
FLIGHT-PATH COMPUTER PROGRAM
By Robert T. Marshall
Flight Research Center
INTRODUCTION
With the expanded flight envelopes of today's aircraft and the performance penalties
associated with nonoptimum flight paths, it is desirable to determine the minimum­
time-to-climb or minimum-fuel-consumed flight paths, or both, for an aircraft. At
present, sophisticated, ground-base computer programs are used to obtain the optimum
flight path between any two points within the flight envelope of an aircraft (refs. 1to 6).
However, the use of these optimization techniques is limited in that they require large
ground-base computers and long computational times and use model atmospheres
that do not always adequately represent the flight environment. In addition, a schedule
for each optimum flight path to be flown must be presented to the pilot before each
flight.
With the recent development of improved computational techniques, such as dynamic
programing methods (ref. 7), and the increased capability of airborne digital com­
puters, the technology now exists to overcome the noted limitations. These developments
make possible the approximate real-time airborne computation and display of an optimum
flight path which applies to the actual atmospheric conditions encountered in flight.
However, for the computation of meaningful flight trajectories, an accurate performance
model, in terms of the climb and acceleration capabilities of the aircraft, is required
together with a means of adjusting the performance model for variations in atmospheric
conditions. It is essential that these two requirements be met, or the capability to
compute a flight path enroute will be of little use to the pilot.
This report presents the results of a flight-test program conducted at the NASA
Flight Research Center to determine the standard-day performance characteristics of
the F-l04G, S/N 56-0790, airplane. These characteristics will be used to investigate
the utilization of an airborne system for the real-time computation of an optimum
flight path. This test program was conducted because it was believed that the available
predicted data (ref. 8), which are for an "average" or typical F-104G airplane, would
not represent the actual performance of the test airplane to the degree of accuracy
required for the computation of meaningful flight trajectories.
The predicted and measured climb and acceleration capability of the test airplane
are compared. In addition, the correction procedures that can be used to adjust the
standard-day data to whatever flight conditions encountered are presented.

SYMBOLS
The standard-day performance data defined in this report were computed in the
U.  S.  Customary System of Units.  The equivalent values in the International System
of Units (SI) are given in parentheses.  Factors relating the two systems are presented
in reference 9.
Drag
drag coefficient,
| cD   |                   |     | qs        |     |     |     |
| ---- | ----------------- | --- | --------- | --- | --- | --- |
| AcD  | drag-due-to-lift  |     | parameter |     |     |     |
7

AcL
­Lift
lift coefficient,
cL
¶S
| D   | total aircraft drag,  |         | lb (N)   |     |     |     |
| --- | --------------------- | ------- | -------- | --- | --- | --- |
| FC  | fuel used,            | counts  |          |     |     |     |
| FD  | fuel density, lb/gal  |         | (kg/m3)  |     |     |     |
| F   | net thrust, lb (N)    |         |          |     |     |     |
n
Fn -
| F   | excess thrust,  |     | D,  lb (N) |     |     |     |
| --- | --------------- | --- | ---------- | --- | --- | --- |
n, ex
| Fu  | fuel used,                                 | lb (kg)  |         |               |     |     |
| --- | ------------------------------------------ | -------- | ------- | ------------- | --- | --- |
| g   | acceleration due to gravity, 32.2 ft/sec2  |          |         | (9.8 m/sec2)  |     |     |
| He  | instantaneous specific energy, ft (m)      |          |         |               |     |     |
| h   | pressure altitude,                         |          | ft (m)  |               |     |     |
|     | altitude posi i,ion-error correction,      |          |         | ft (m)        |     |     |
AhPC
2
--
1
|     |     |                      | IIT1111111111        | I I  111111111 11111111111  | ~IIII11111111 1111mII I I  | I11111111111  |
| --- | --- | -------------------- | -------------------- | --------------------------- | -------------------------- | ------------- |
|     |     | I .1111-..1-11.1ll1  | 11111111 II I1111..  |                             |                            |               |

| K   | calibration constant
      |     |              |
| --- | --------------------------- | --- | ------------ |
| M   | Mach number
               |     |              |
| AM  | Mach number position-error  |     | correction
 |
PC
|     | ambient pressure, in.  |     | Hg (N/m2)
 |
| --- | ---------------------- | --- | ----------- |
compressor inlet total pressure, in.  Hg (N/m2)

P
t2
dynamic pressure, lb/ft2 (N/m2)

4

|     | instantaneous climb potential,  |     | ft/min (m/sec)
 |
| --- | ------------------------------- | --- | ---------------- |
R/C
| S   | wing reference area, ft2 (m2)
 |     |                      |
| --- | ------------------------------- | --- | -------------------- |
|     | ambient temperature,            |     | "F ("C) or "C (OK)
 |
Ta
|       | fuel temperature,       |                           | ("C) or "C (OK)
 |
| ----- | ----------------------- | ------------------------- | ----------------- |
| Tf    |                         | O                         | F                 |
|       | total temperature,      |                           | ("C) or "C (OK)
 |
| Ttot  |                         | O                         | F                 |
| t     | time,                   | sec
                     |                   |
| V     | velocity,               | knots or ft/sec (m/sec)
 |                   |
| W     | airplane gross weight,  |                           | lb (kg)
         |
|       | fuel flow,              | lb/sec  (kg/sec)
        |                   |
wf
change in specified parameter

3

1I11I  I  I  I  11111111111lll11l1
Pt2
-
| 6   | compressor inlet total-pressure  | ratio,  |
| --- | -------------------------------- | ------- |
29.92  (&O)
t2
Subscripts :
/
| ab  | afterburner
                |     |
| --- | ---------------------------- | --- |
| e   | main engine
                |     |
| es  | engine start
               |     |
| i   | indicated
                  |     |
| ic  | instrument corrected value
 |     |
| id  | induced drag
               |     |
standard-day  condition

S

true value

T
| t   | test-day  condition
 |     |
| --- | --------------------- | --- |
tot a I va 1ue

tot
| W   | weight correction
 |     |
| --- | ------------------- | --- |
AIRPLANE DESCRIPTION
The performance flight-test program was conducted with the F-104G prototype
airplane, S/N  56-0790  (fig. l), a modified F-104A  airplane.  Although the airplane
is a modified F-104A  airplane, the basic external dimensions, surface areas, and
control systems are those of an F-104G  airplane.  A three view drawing of the F-104G
airplane is shown in figure 2, and pertinent physical characteristics are given in
The airplane is described in detail in reference 8.
table 1.
4

I
.-

The airplane is powered by a General Electric J79-GE-llA engine, a high-pressure-
ratio, single-rotor , afterburning turbojet engine. The entire flight-test program was
conducted with one engine. The engine required no retrimming during the program.
A detailed description and minimum performance characteristics of the engine are
included in reference 10.
INSTRUMENTATION
The instrumentation installed in the test airplane for this program included a
photopanel, a self-recording three-component accelerometer, a test nose boom, and
two precision volumetric flow meters. The photopanel shown in figure 3 was installed
in the nose compartment and was equipped with a 16-millimeter camera which was
pulsed at 1 frame per second for all data runs. The photopanel was also equipped
with a time-code generator which was set prior to each flight to give the time of day.
The parameters displayed on the photopanel and the instrument operating ranges and
resolutions were as follows:
Parameter Range Resolution
Indicated airspeed. knots . . . . . . . . . . . . . . . 0 to 800 *o. 5
Indicated pressure altitude, ft (m) . . . . . . . . . . 0 to 60,000 (0 to 18,288) 15 (.t 1. 52)
Angle of attack. deg (rad). . . . . . . . . . . . . . . - 5 to 20 (-0. 087 to 0.349) io.5 (LO. 0087)
Engine rpm. percent . . . . . . . . . . . . . . . . . 0 to 100 il
Exhaust gas temperature. "C ("K) . . . . . . . . . . 0 to 1000 (273. 16 to 1273. 16) i5 (t5)
Fuel used (engine). counts' . . . . . . . . . . . . . . 0 to 9999.9 *o. 1
Fuel used (afterburner), counts2 . . . . . . . . . . . 0 to 9999.9 *o. 1
Fuel temperature (engine). "C (OK) . . . . . . . . . 0 to 200 (273. 16 to 473. 16) 12.5 (t2.5)
Fuel temperature (afterburner). "C . . . . . . 0 to 250 (273. 16 to 523. 16) *2. 5 (t2.5)
(OK).
Throttle angle, deg (rad) . . . . . . . . . . . . . . . 0 to 100 (0 to 1.745) +O. 5 (io,0087)
Outside air stagnation temperature, "C ("K). . . . . -30 to 150 (243. 16 to 423. 16) *l (*l)
Horizontal stabilizer position. deg (rad) . . . . . . . 5 to -17 (0. 087 to 0.297) +O. 5 (*O. 0087)
Ti me _ _ _ _ _ - - _ - _ - - - - _ - Hours, minutes, seconds
'I count = 5.67 gal (0.02146 m3)
*I count = 12.57 gal (0.04758 m3)
The self-recording three-component accelerometer was installed as close to the
airplane center of gravity as possible. The recording unit had a film speed of
0.75 in. /sec (0.019 m/sec). The ranges and resolutions of the three accelerations are
tabulated on the following page. For correlation, the photopanel time code was recorded
as a pulse type of signal (IRIG E format) on the film.
5

|                               | Parameter  |         | R ange      | Resolution  |
| ----------------------------- | ---------- | ------- | ----------- | ----------- |
|                               |            | . .     | . . . . .   |             |
| Longitudinal acceleration, g  |            |         | -+1         | &O. 005     |
|                               |            | . . . . | . . . . .   | *o.         |
| Normal acceleration,          |            | g       | -1 to 4     | 01          |
|                               |            | . . . . | . . . . .   |             |
| Lateral acceleration,         |            | g       | ktl         | &O.  005    |
Time  . . . . . . . . . . . . . . . . . . .  - - - - Hours, minutes , seconds
The test-day  ambient temperature at altitude was obtained from a weather balloon.
The balloon passed through the test altitudes within 90 minutes of the actual flight
time and within 50 miles (80.5 kilometers) of the actual flight path.  The accuracy of
| these temperature data is &2O  |     | C (*2'  | K).  |     |
| ------------------------------ | --- | ------- | ---- | --- |
A test nose boom with a standard NACA Pitot-static  probe (ref, 11) was installed
on the airplane.
|     | STATIC-PRE SSURE POSITION-ERROR  |     |     | CALIBRATION  |
| --- | -------------------------------- | --- | --- | ------------ |
Before the performance data were analyzed, it was necessary to obtain a position-
error calibration for the test airplane , because the static-pressure  source during
flight testing is usually not in a position at which the pressure is ambient.  Therefore,
corrections are required to determine the true (ambient) pressure so that true Mach
number and true pressure altitude may be computed.
The position-error  calibration was determined from tower flyby data and from
FPS-16 precision radar tracking data obtained during accelerations and decelerations
at constant altitudes.  For these data runs an ambient pressure was required for
comparison with the measured pressure at the static source,  For the tower flyby
runs a precise barometer located in an adjacent tower provided the true ambient
pressure, then theoretical adjustments were made for the small differences in elevation
between the airplane and the tower.  For the acceleration and deceleration runs,  a
combination of precision  FPS-16 radar tracking data and radiosonde balloon data was
used to compute the correct ambient pressure.  Figures 4and 5 are the position-error
calibration curves used to determine the true Mach number and true pressure altitude
from the indicated measurements,
TESTS
Nonsteady-state  (dynamic) performance test methods were used to determine the
performance of the test airplane.  The test data were obtained for level-flight
accelerations and for constant-Mach-number  climbs at maximum power and at a
The speed and altitude information obtained was used to determine
constant heading.
the total energy of the airplane,  which is the sum of the potential and kinetic energy
at a given point in the flight envelope.  The rate of  change of  the total energy per unit
time for the airplane is a measure of the climb potential (specific excess power) of
the vehicle.
6

The test conditions selected for the level-flight accelerations and the constant-
Mach-number climbs are presented in table 2. The flight-test conditions were
selected to provide performance data for most of the operating envelope of the test
airplane. The airplane was flown in a clean configuration (landing gear and flaps
retracted and no external stores) for all test conditions. In addition, the airplane's
center of gravity was allowed to travel along a normal schedule, because the range
of this variable for the tests was such that it would not affect the results.
DATA ANALYSIS
The flight-test performance data of an aircraft are easily obtained from the
measured test-day data, but this information has little meaning when parameters
from flights flown on different days are compared. To avoid this problem, it is
necessary to reduce the flight-test results to those which would have been'obtained
if the flights were flown under ideal standard-day conditions.
Specific-energy analysis methods (refs. 12 to 14) were used to compute the test-
day performance data and to standardize the data to an airplane gross weight of
18,000 pounds (8165 kilograms) and the 1962 U. S. Standard Atmosphere. The data
analysis methods used for computing and applying the standardization correction factors
are discussed in detail in the appendix. The analysis methods are general (in a
mathematical sense), in that they can be applied to correct a given set of data to any
appropriate set of reference conditions. It therefore follows that these analysis
methods can be used equally well to calculate the performance of the airplane for any
given nonstandard day from the normalized standard-day data, and, similarly, these
methods provide adjustments which compensate for variations in weight from a
standard weight.
RESULTS AND DISCUSSION
Excess Thrust
The standard-day variation of excess thrust with increasing Mach number for the
test airplane as determined from the level-flight acceleration data is presented in fig­
ures 6(a) to 6(e) for altitudes of 10,000 feet (3048 meters) to 50,000 feet (15,240 meters)
at 10,000-foot (3048-meter) intervals. Two acceleration runs (A and B) were flown at
each altitude with different atmospheric conditions and airplane gross weights for each
run.
To provide some insight into the excess-thrust data, a schematic of typical F-104G
thrust and drag curves (ref. 15) is presented in figure 7 for the test altitudes at a
constant airplane weight. From figure 7, the qualitative relationship between the
-
thrust, Fn, drag, D, and therefore the excess thrust, Fn D, can be seen as a
function of Mach number and altitude.
Figure 7 shows that in level flight at subsonic speeds the thrust increases almost
linearly with Mach number. As indicated by the crosshatched regions, as the speed
7
I

increases in the subsonic region, the excess thrust increases from some initial level
to a maximum and then rapidly decreases as the transonic drag rise is encountered.
The flight-test data in figures 6(a) to 6(d), as expected, clearly show this subsonic
variation of excess thrust with Mach number,
At supersonic speeds, as shown in figure 7, the variation of excess thrust with
increasing Mach number is dependent on the altitude at which the airplane is operating.
For example, the excess thrust decreases as the Mach number increases above 1.0
at an altitude of 10,000 feet (3048 meters). Conversely, excess thrust increases with
supersonic Mach numbers at an altitude of 50,000 feet (15,240 meters). The flight-test
data in figures 6(a) to 6(e) show the variation of excess thrust with altitude and super­
sonic Mach number.
For altitudes of 20,000 feet (6096 meters) and greater, the thrust increases sharply
when a 579 engine operating characteristic known as 'ITa reset" is encountered, as
illustrated in figure 7. T reset advances the engine rpm by 4 percent to improve the
2
engine stall margin at compressor inlet temperatures greater than 194" F (90° C).
This advance in rpm also increases the maximum available thrust of the engine, which
in turn accounts for an increase in the excess thrust of the airplane, as shown.
T2
reset is discussed in detail in reference 15.
The effect of T2 reset on the data of this study can be seen in figures 6(b), 6(c),
and 6(d) as an increase in the excess thrust at Mach numbers of 1.50, 1.72, and 1.95,
respectively. Although T reset would ordinarily be expected to occur as indicated in
2
figure 7 for an altitude of 50,000 feet (15,240 meters), figure 6(e) does not show an
increase in excess thrust due to T2 reset, because the colder-than-standard ambient
temperatures encountered during the level accelerations at this altitude caused a delay
in the activation of T2 reset until Mach 2. 0.
Fuel Flow
Figure 8 presents the standard-day , maximum-power fuel-flow rates for the
J79-GE-llA engine installed in the test airplane. As expected, the fuel flow increases
with increasing Mach number for a given altitude and decreases with increasing altitude
for a given Mach number. When T reset is encountered, the fuel-flow rate increases
2
rapidly for Mach numbers greater than 1.50, 1.72, and 1.95 at altitudes of 20,000 feet
(6096 meters), 30,000 feet (9144 meters), and 40,000 feet (12,192 meters), respectively.
Climb Potential
The standard-day climb potential (or specific excess power) of the test airplane as
determined from the level-flight acceleration data is presented in figures 9(a) to 9(e)
for altitudes of 10,000 feet (3048 meters) to 50,000 feet (15,240 meters) at 10,000-foot
(3048-meter) intervals, As expected, the variation of climb potential with increasing
Mach number and altitude is similar to the trends of the curves of excess thrust
presented in figure 6.
8

The relationship between excess thrust and climb potential, (R/C),, is given by the
following rearranged version of equation (19) of the appendix:
In the data analysis the gross weight, W,, was a constant, and the climb potential-is,
therefore, directly proportional to the product of the excess thrust and true velocity,
, of the airplane. Thus, at a constant altitude the differences between the
vT, s
characteristics of the curves of climb potential presented in figure 9 and the curves
of excess thrust presented in figure 6 are due to the effects of the true velocity on the
climb potential.
The true velocity at a constant altitude is a linear function of Mach number. Its
effect on the climb potential can be seen by comparing the excess-thrust and climb-
s(~),
potential data in figures 6(c) and respectively. As shown, above Mach 1.0 the
excess-thrust data remain fairly constant, though increasing slightly; whereas , the
climb-potential data increase significantly because of the increasing value of the true
velocity. Although present, the effects of true velocity on the climb-potential data
are not as evident for altitudes of 20,000 feet (6096 meters), 40,000 feet (12,192 meters),
and 50,000 feet (15,240 meters) as for 30,000 feet (9144 meters).
Comparison of Predicted and Flight-Test Data
In the initial phase of the test program, it was assumed that the predicted perform­
ance data would not represent the actual performance of the test airplane to the degree
of accuracy required to compute meaningful flight trajectories. To evaluate this
assumption, the predicted climb-potential data were computed and are presented in
figure 9 as dashed lines. The data were computed from the standard F-104G perform­
ance characteristics (ref. 8) and do not include the effects of T2 reset discussed
previously.
For the predicted data to adequately represent the performance capability of the
test airplane, it was believed that the difference between the predicted and test values
of climb potential should not be greater than 10 percent at any point within the flight
envelope. As shown in figure 9, the flight-test and predicted data do not agree within
10 percent over a significant portion of the flight envelope.
As a crosscheck of the level-acceleration data presented in figure 9, quasi-constant
Mach number climbs were flown at the Mach numbers listed in table 2. The standard-
day constant-Mach-number-climb performance data (climb potential and fuel-flow rate)
presented in figures 10 and 11 were crossplotted in figures 8 and 9. The differences
between the level-acceleration and climb data are attributed to the difficulty in
establishing and holding the climb speed in the constant-Mach-number climbs because
of the high climb rates encountered at the lower altitudes. As a result, the values of
climb potential computed for the climb data are somewhat in error. These data are
used, then, only for a qualitative crosscheck of the more accurate level-acceleration data.
9

Application of Flight-Test Results
The level-acceleration flight-test data presented in figure 9 were used to define a
computer model in terms of excess thrust and fuel flow for the performance of the test
airplane. This computer model was then used with the RUTowski OPtimization
Computer Program (ref. 6) to generate a complete climb-potential map for the test
airplane. This map, presented in figure 12, consists of lines of constant-climb
potential plotted against true velocity and altitude. Figure 12 also presents a complete
picture of the total performance capability of the test airplane.
The flight-test data and the data-analysis procedures used defined an accurate
computer model for the computation of meaningful flight trajectories and provided a
means of adjusting the performance model for variations in atmospheric conditions,
But this information is still cumbersome to use in a real-time flight-path-optimization
system because of the time required to compute and apply the correction factors to the
performance model for the deviations in atmospheric conditions.
It would be highly desirable for a computer model to be defined in terms of the
specific values of thrust and drag (that is, not just the difference between thrust and
drag) for the entire flight envelope of an airplane. Then the correction factors required
to adjust the performance model for variations in atmospheric conditions could be
computed easily and applied directly to the values of thrust and drag. However, the
large number of flight tests and the extensive instrumentation required to define such
a model make this approach inefficient in terms of the cost and time required. There­
fore, methods and techniques are needed for developing a computer model, in terms
of thrust and drag, from test data so that data from a few flight tests can be used to
define the performance for the entire flight envelope of any aircraft.
CONCLUDING REMARKS
A flight-test investigation was conducted to determine the performance characteristics
of the F-l04G, S/N 56-0790, airplane and to define a computer model for the perform­
ance of the airplane.
The climb-potential (specific excess power) data obtained from the flight tests were
compared with available predicted performance data for the "average" or "typical"
F-104G airplane, It was found that the predicted data did not represent the actual
performance of the test airplane to the degree of accuracy required to compute
meaningful flight trajectories. Therefore, the flight-test excess-thrust and fuel-flow
data obtained were used to define an accurate performance model for the test airplane
for a standard day at maximum afterburner power.
Even though the standardized flight-test data defined an accurate computer perform­
ance model, it would also be highly desirable for a computer model to be defined in
terms of the specific values of thrust and drag �or an entire flight envelope. However,
the cost and time required for the large number of flight tests and the extensive
instrumentation required to define such a model make this approach inefficient. Thus ,
there is a need for methods and techniques for developing a computer performance
10

model from test data so that data from a few flight tests can be used to define the
performance for the entire flight envelope of an aircraft.
Flight Research Center,
National Aeronautics and Space Administration,
Edwards, Calif., January 29, 1971.
11
1 .-.
.,
..- .-..".
, ,, ,., , ......................................

APPENDIX
DATA-ANALYSIS PROCEDURES
To correct the test-day data to standard-day conditions, a digital computer program
was written to calculate the standard-day performance data from the level-flight­
acceleration and constant -Mac h-number -climb flight data, using specific-energy analysis
methods of references 12 to 14. The procedure used to compute the standard-day data
is outlined in the following discussion.
By using the flight-test-data input and the following equations, the standard-day
climb-potential, excess-thrust, and fuel-flow data were computed for the test airplane
for level-flight accelerations and constant-Mach-number climbs. The initial phase of
the data analysis was the computation of the test-day performance of the airplane.
The indicated Mach number for each data point was determined from the values of
indicated airspeed and indicated altitude corrected for instrumentation calibration
errors as follows:
hit)
Mic = f(Vic, (1)
The detailed equations for the calculation of the indicated Mach numbers are given in
reference 12.
The true Mach number and true pressure attitude were determined from the
indicated Mach number and the airspeed position-error curves (figs, 4 and 5) as follows:
The true test-day velocity, in knots, was then found by using the expression
VT, = 38. 9 6 9 M T d G (4)
with Ta, obtained from the weather-balloon data in "C and changed to The
OK.
value of VT, was changed to feet/second (meters/second), and the instantaneous
specific energy for the airplane at the test-day conditions was determined by using
the equation
pbe)
He=hT,t+(v T t
(5)
The instantaneous value of climb potential at the test weight and thrust and with
zero acceleration was obtained by determining the slope, at each test point, of a
12
I

APPENDIX
smooth curve fitted to a time history of He as follows:
The engine and afterburner fuel-used values for each data point were determined
from the following equations :
FU, = FC.(K)(FD,) (7)
with the engine and afterburner fuel densities determined by
where K is a calibration constant.
The instantaneous total fuel used was then determined by using the expression
The instantaneous airplane weight was determined by subtracting the total fuel used
from the airplane weight at engine start as follows:
The instantaneous fuel flow was obtained by determining the slope, at each point,
of a smooth curve fitted to the time history of the total fuel used for each data run,
that is,
After the test-day data were computed, the following equations were used to correct
13

APPENDIX
the test data to the selected standard-day conditions. Corrections were applied for
the nonstandard-day temperature effects on the altitude , true airspeed, thrust, and
fuel flow and for the nonstandard weight effects on the airplane’s inertial and induced
drag.
For a given level-flight acceleration, the selected test altitude was the altitude
to which the data were standardized. The standard-day temperature and pressure
were then computed for the selected standard altitude as follows:
The exact equations used to compute these quantities are given in reference 12. For
the constant-Mach-number-climb data, Ta, and p were computed as a function
a, s
The standard-day true velocity, Vt, s, in knots, was then calculated from
Of hT, t-
equation (4)substituting T for TaYt.
a, s
The change in thrust, AF,, resulting from nonstandard-day temperatures was
A- - Fn
00
tt22 --
oobbttaaiinneedd kkoomm aa pplloott ooff vveerrssuuss tteesstt--ddaayy ttoottaall temperature. The data
--
TTTTyySS TTTT,,tt
for this plot were obtained from reference 8. The change in thrust was then computed
as follows:
AFn
-L
“n = TT, - T ~ ,(TT, S - TT, t) (%2)
The correction to the test-day climb potential for the nonstandard-day temperature
effects on thrust, A(R/C)power, was then determined by using the equation
Corrections were then applied to correct the test-day airplane weight to a standard
weight. The weight correction was divided into two portions. The first portion was
the inertia correction, A(R/C)w, and was determined with the expression
14

APPENDIX
It should be noted that the temperature corrections for true velocity and geometric
-T. a t
altitude for a constant test-day Mach number are included in The second portion
Ta, s
of the weight correction was the induced-drag correction, h(R/C)id, which was
determined as follows :
where
which is the change in the induced-drag coefficient. Combining the above corrections,
the standard-day climb potential was determined by
The value of V was changed to feet/minute (meters/second), and the standard-
T, s
day excess thrust was computed by
The change in fuel flow, AWf, for nonstandard-day temperatures was determined
AWf
6
t2
from a plot of versus the test-day total temperature. The data for the
TT, S - TT, t
plot were obtained from reference 8. The change in fuel flow is then computed as
follows:
15

APPENDIX
AWf
The fuel flow was then corrected to the standard-day conditions by using the
expression
For the level-flight acceleration data the values of (R/C),, F,,,,, and Wf
were plotted against Mach number for each of the selected standard-day altitudes.
For the climb data the values of (R/C),, Wf, s, and MT, t were plotted against altitude
for each climb schedule flown.
16

REFERENCES
1.  Bryson, A.  E. ; and Denham, W.  F. : A Steepest-Ascent  Method for Solving
Optimum Programming Problems.  J. Appl.  Mech.,  vol.  29,  series E, no.  2,
| June 1962, pp.  |     | 247-257.  |     |     |     |
| --------------- | --- | --------- | --- | --- | --- |
Joel W. : STOP -
2. 	 Stein,  Lawrence H. ; Matthews,  Malcolm L. ; and Frenk,  A
Computer Program for Supersonic Transport Trajectory Optimization.  The
| Boeing Co.  | (NASA CR-793),  |     | 1967.  |     |     |
| ----------- | --------------- | --- | ------ | --- | --- |
3. 	 Mobley,  R.  L. ;and Vorwald, R.  F. : Three-Degree-of  Freedom Problem
Optimization Formulation.  Volume 3.  User's  Manual.  Tech.  Doc.  Rep.  No.
FDL-TDR-64-1,  Part 11,  Volume 3, Air Force Flight Dynamics Lab. ,
| Wright-Patterson  |     | Air Force Base,  |     | Ohio,  June 1964.  |     |
| ----------------- | --- | ---------------- | --- | ------------------ | --- |
4. 	 Schmidt, H.  E. ; Helgason, R.  V. ;Witherspoon,  J. T. ; and Geib, K.  E. :
Trajectory Optimization by Method of Steepest Descent.  Volume I11 Programmer's
Manual.  Tech.  Rep.  AFFDL-TR-67-108,  Air Force Flight Dynamics Lab.,
| Wright-Patterson  |     | Air Force Base,  |     | Ohio, April 1968.  |     |
| ----------------- | --- | ---------------- | --- | ------------------ | --- |
Lamb,  George H. : Validation of the Energy-Maneuverability  Theory - Optimum
5.
Flight Path for the F-4C  Aircraft.  Tech.  Rep.  APGC-TR-66-27,  Air Proving
Ground Center, Eglin Air Force Base, Fla. , April 1966.
Porter, Milton B. , Jr. : RUTOP-Rutowski 2timization Computer Program.
6.
Tech.  Rep.  FTC-TR-68-14,  Air Force Flight Test Center,  Edwards Air Force
| Base,  | Calif. , Jan.  | 1969.  |     |     |     |
| ------ | -------------- | ------ | --- | --- | --- |
7. 	 Bellman, Richard; and Kalaba,  Robert:  Dynamic Programming and Modern
| Control Theory.  |     | Academic Press Inc., N.  |     | Y. , c. 1965.  |     |
| ---------------- | --- | ------------------------ | --- | -------------- | --- |
8. 	 Avant,  N.  J. : Performance Characteristics - Appendix A.  Rep.  No.  16097 App.  A,
| Lockheed Aircraft Corp.,  |     |     | July 16, 1962.  |     |     |
| ------------------------- | --- | --- | --------------- | --- | --- |
A. : The International System of Units -
| 9. 	 Mechtly,        | E.  |                |     |        | Physical Constants and  |
| -------------------- | --- | -------------- | --- | ------ | ----------------------- |
| Conversion Factors.  |     | NASA SP-7012,  |     | 1969.  |                         |
10. 	 Michaels,  J. M. ; Wesling,  G.  C. ; Housley,  F.  R. ; and Henderson, R.  L. :
J79-GE-7,  J79-GE-11,  J79-GE-llA  Turbojet Engine.  R60FPD45l.  Flight
| Propulsion Div. , General Electric, Sept.  |     |     |     | 1960.  |     |
| ------------------------------------------ | --- | --- | --- | ------ | --- |
11.  Richardson,  Norman R. ; Pearson, Albin 0. : Wind-Tunnel  Calibrations of a
Combined Pitot-static  Tube,  Vane-Type  Flow-Direction  Transmitter , and
Stagnation-Temperature  Element at Mach Numbers From 0.60 to 2.87.  NASA
| TN D-122,  | 1959.  |     |     |     |     |
| ---------- | ------ | --- | --- | --- | --- |
12.  Herrington,  Russel M. ; Shoemacher, Paul E. ; Bartlett, Eugene P. ; and Dunlap,
Everett W. : Flight Test Engineering Handbook.  Tech.  Rep.  No.  6273, Air
| Force Flight Test Center, May 1951 (rev. Jan.  |     |     |     |     | 1966).  |
| ---------------------------------------------- | --- | --- | --- | --- | ------- |
17

I I I I I I I I1 IIIIII 1l11l1l1~ll111111l111
13. Godwin, 0. D. ; Frazier, F. D. ; and Durnin, R. E. : Performance Flight Test
Techniques. FTC-TIH 64-2006, USAF Aerospace Research Pilot School,
Edwards Air Force Base, Calif.
14. Hendrix, George D. ; Godwin, Orgle D. ; Frazier, Frank D. ;and Durnin, Rodney
E. : Performance Flight Testing Theory. FTC-TIH 64-2005, USAF Aerospace
Research Pilot School, Edwards Air Force Base, Calif.
15. Anon. : Flight Manual F/RF/TF-l04G. T. 0. 1F-104G-1, U. S. Air Force,
pp, 1-12 (rev. July 1968), pp. 6-11 (rev. Oct. 1967).
18

TABLE 1.-PERTINENT  PHYSICAL CHARACTERISTICS OF THE TEST AIRPLANE
General:
|                  | . . . | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .   |                |
| ---------------- | ----- | --- | ------- | --------- | --- | ----- | ----- | --------- | ----- | -------------- |
| Length, ft (m)   |       |     |         |           |     |       |       |           |       | 54.77 (16.69)  |
|                  | . . . | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .   |                |
| Height,  ft (m)  |       |     |         |           |     |       |       |           |       | 13.49 (4.11)   |
Wing:
|                 | . .     | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .   |                |
| --------------- | ------- | --- | ------- | --------- | --- | ----- | ----- | --------- | ----- | -------------- |
| Area, ft2(m2).  |         |     |         |           |     |       |       |           |       | 196. 1 (18.2)  |
|                 | . . . . | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .   |                |
| Span, ft (m)    |         |     |         |           |     |       |       |           |       | 21.94 (6.69)   |
|                 | . .     | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .   |                |
| Aspectratio..   |         |     |         |           |     |       |       |           |       | 2.45           |
Fuselage:
|                          |       |     | . . . . | . . . .   | . . . | . . . | . . . | . . . . . | . .   |                |
| ------------------------ | ----- | --- | ------- | --------- | ----- | ----- | ----- | --------- | ----- | -------------- |
| Frontal area, ft2 (m2).  |       |     |         |           |       |       |       |           |       | 25. 00 (2. 3)  |
|                          | . . . | . . | . . . . | . . . .   | . . . | . . . | . . . | . . . . . | . .   |                |
| Length,  ft (m)          |       |     |         |           |       |       |       |           |       | 51.25 (15.62)  |
|                          | . . . | . . | . . . . | . . . . . | . .   | . . . | . . . | . . . . . | . .   |                |
| Fineness ratio           |       |     |         |           |       |       |       |           |       | 9.09           |
Horizontal tail:
|                         | . . .   | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .     |                |
| ----------------------- | ------- | --- | ------- | --------- | --- | ----- | ----- | --------- | ------- | -------------- |
| Area, ft2 (m2)          |         |     |         |           |     |       |       |           |         | 48.2 (4. 5)    |
|                         | . . . . | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .     |                |
| span, ft(m)             |         |     |         |           |     |       |       |           |         | 11.91 (3, 63)  |
|                         | . . . . | . . | . . . . | . . . . . | . . | . . . | . . . | . . . . . | . .     |                |
| Aspect ratio            |         |     |         |           |     |       |       |           |         | 2.95           |
|                         |         | .   | . . . . | . . . .   | . . | . . . | . .   | . . .     |         |                |
| Deflection, deg (rad).  |         |     |         |           |     |       |       | 5 to -17  | (0.087  | to -0.297)     |
Weight:
|                  | . . . | . . | . . . . | . . . . . | . .   | . . . | . . . | . . . . . | . .   |                |
| ---------------- | ----- | --- | ------- | --------- | ----- | ----- | ----- | --------- | ----- | -------------- |
| Basic,  lb (kg)  |       |     |         |           |       |       |       |           |       | 13,608 (6172)  |
|                  | . . . | . . | . . . . | . . . . . | . .   | . . . | . . . | . . . . . | . .   |                |
| Pilot, Ib(kg).   |       |     |         |           |       |       |       |           |       | 230 (104)      |
|                  | . . . | . . | . . . . | . . . . . | . .   | . . . | . . . | . . . . . | . .   |                |
| Fuel, Ib(kg).    |       |     |         |           |       |       |       |           |       | 6228 (2825)    |
|                  | . . . | . . | . . . . | . . . .   | . . . | . . . | . . . | . . . . . | . .   |                |
| Total, lb (kg)   |       |     |         |           |       |       |       |           |       | 20,066 (9102)  |
19

|                    | TABLE 2. -FLIGHT-TEST  | CONDITIONS  |                    |             |
| ------------------ | ---------------------- | ----------- | ------------------ | ----------- |
|                    |                        | I  I        |                    |             |
|                    | Power                  | Test runs   | Altitude,  ft (m)  |             |
| Flight conditions  |                        |             |                    | Mach range  |
|                    |                        | I  I        |                    |             |
0.5 to 1.2
|     |     | 2   | 10,000 (3048)  |               |
| --- | --- | --- | -------------- | ------------- |
|     |     | 2   | 20,000 (6096)  | 0. 6 to 1. 6  |
Maximum
| Level acceleration  | after­ | 2   | 30,000 (9 144)  | 0. 6 to 1.9  |
| ------------------- | ------ | --- | --------------- | ------------ |
burner
|     |     | 2   | 40,000(12, 192)  | 0.8 to 2. 0  |
| --- | --- | --- | ---------------- | ------------ |
|     |     | 2   | 50,000 (15,240)  | 1.4 to 2. 0  |
I
0. 6
to ceiling
I
|     |     | 1   | 5000 (1524)  | 0.7  |
| --- | --- | --- | ------------ | ---- |
to ceiling
|     | I   | I   |              |        |
| --- | --- | --- | ------------ | ------ |
|     |     | 2   | 5000 (1524)  | 0. 75  |
to ceiling
I
Maximum
| Constant-Mach­ |     | 2   | 5000 (1524)  | 0. 90  |
| -------------- | --- | --- | ------------ | ------ |
after­
| number climb  |     | 1   | to ceiling  |     |
| ------------- | --- | --- | ----------- | --- |
burner
1
|     |     |     | 30,000(9144)  | 1.5  |
| --- | --- | --- | ------------- | ---- |
to ceiling
I
|     |     | 1 	 | 30,000 (9144)  |     |
| --- | --- | --- | -------------- | --- |
1. 85
to ceiling
I
35.000 (10,668)
|     |     | 1 	 |     | 1. 95  |
| --- | --- | --- | --- | ------ |
to ceiling
20

Figure 1. F-104G, S/N 56-0790, test airplane.

N
N
\ /I ‘7
I Y ,
I
4
54.77
(16.69)
/ \ \ 1132. 4A90
(4.11)
t
ine
4
L-21.94
(6.69)
Figure 2. Three-view drawing of the F-104G airplane. Dimensions in feet (meters).

to
w Figure 3. Photopanel installed in test airplane. E-19582

|     | o 	 Radar  |     |
| --- | ---------- | --- |
Tower flyby
F
*.0056
AMpc correction to be added
-

-.01

| Figure 4.  | Position-error  | calibration for Mach number.  |
| ---------- | --------------- | ----------------------------- |

- 600
1600 - - 500
-
-
400
-
1200
-
Ahpc correction 300 Ahpc correction
-
to beadded, ft 800 200 to be added, m
-
-
400
100
-
0 0
-
-100
-400
Figure 5, Position-error calibration for altitude.

| 3   |     |     |     |     |     | f   |
| --- | --- | --- | --- | --- | --- | --- |
15
|     |     |     |     |     | Run   | 60  |
| --- | --- | --- | --- | --- | ----- | --- |
|     |     |     |     |     | o A   |     |
|     |     |     |     |     | O B   |     |
1c
40
F Ib
n, ex’
F  kN
n, ex’
0
5
20
|     |     |     | 1   | 1   | I   | I  o
 |
| --- | --- | --- | --- | --- | --- | ------ |
|     | I   | 1   |     |     |     |        |
01
.4  .6  .8  1.0  1.2  1.4  1.6

M

|     |     | (a)  Altitude = 10,000 ft (3048 m)
 |     |     |     |     |
| --- | --- | ------------------------------------ | --- | --- | --- | --- |
15: 103
Run
|     |     |     |     | o A    |     |     |
| --- | --- | --- | --- | ------ | --- | --- |
|     |     |     |     | O B
 |     |     |
10
Fn, ex7  Ib
5
|     |     |     |     | I   | I   |     |
| --- | --- | --- | --- | --- | --- | --- |
| 0   |     | 1   | I   |     |     |     |
.6  .8  1.0  1.2  1.4  1.6
M
(b) Altitude = 20,000 ft (6096 m).
Figure 6.  Standard-day excess thrust for the test airplane obtained from
flight at a normal load factor of  1, maximum afterburner power, gross
weight of 18,000 pounds (8165 kilograms), and with no external stores.
26

10x103
Run
-40
o A
O B
0
(c) Altitude = 30,000 ft (9144 m).
-30
Run
o A
O B
01 1 1
.8 1.0 1.2 1.4 1.6 1.8 2.0 2.2
M
(d) Altitude = 40,000 ft (12,192 m).
Figure 6. Continued.

30
Run
o A
20
4.
Fn, ex, kN
Fn, ex7 Ib
10
0
1.0 1.2 1.4 1.6 1.8 2.0 2.2
M
(e) Altitude = 50,000 ft (15,240 m),
Figure 6. Concluded.
28
I

Maximum net thrust, Fn
---
Airplane drag, D
iZ7Z77 Excess thrust, Fn - D
h, ft (m)
10, OOO (3048)
L T ~reset effect
(9144)
Thrust and drag
000 (12, 196)
000 (15,240)
.6 1.0 2.0
M
Figure 7. Schematic of typical thrust and drag curves (ref. 15) for the test
airplane at maximum afterburner power and constant gross weight.
29

h, ft (m)
w
0 0 10, 000 (3048)
20,000 (6096)
0
0 30,000 (9144)
A 40,000 (12,192)
50,000 (15,240)
Open symbols - level-flight acceleration
Solid symbols - constant M climb
6
12
5
- 4
lo8[-
-3 Wf, kglsec
Wf, lblsec 6k­
-2
4­
2- A A ' -1
.4 .6 .8 1.0 1.2 1.4 1.6 1.8 2.0 2.2
M
Figure 8. Standard-day fuel flow for the J79-GE-llA engine installed in the test airplane at maximum
afterburner power.

Run
|     |     |     |     | o A                  |     |     |
| --- | --- | --- | --- | -------------------- | --- | --- |
|     |     |     |     | O B                  |     |     |
|     |     |     |     | 0  Constant M climb  |     |     |
40x103
-200
30-
-150
| Climb potential,  | ftlmin 20,­ |     |     |     | 4  Climb potential,  | mlsec  |
| ----------------- | ----------- | --- | --- | --- | -------------------- | ------ |
100
|     | lot  |     |     |     | i 5 0   |     |
| --- | ---- | --- | --- | --- | ------- | --- |
0
.4  .6  .8  1.0  1.2  1.4
M
(a) Altitude = 10,000 ft (3048 m).
Figure 9.  Standard-day climb potential for the test airplane obtained from level-flight  accelerations at a
normal load factor of 1, maximum afterburner power, gross weight of  18,000 pounds (8165 kilograms),
and with no external stores.

30x10~ 0
w
to
4
100
Climb potentia I, ftlmin Climb potential, mlsec
-50
O B t-+
T2 reset
0 Constant M climb
.6 .8 1.0 1.2 1.4 1.6 1.8
M
(b) Altitude = 20,000 ft (6096 m)
Run
3OjdO3 o A
I
O B
n
0 Constant M climb
-
20
Climb potential, 1 Climb potential,
ftlmin mIsec
-50
(e) Altitude = 30,000 ft (9144 m).
Figure 9. Continued.

|     | Run  |     |     |     |     |     | -150 |     |
| --- | ---- | --- | --- | --- | --- | --- | ---- | --- |
30x10~
o A
t---
|     | O B  |     |     |     |     | T2 reset  |     |     |
| --- | ---- | --- | --- | --- | --- | --------- | --- | --- |
0  Constant M climb
20 -
-100
Climb potentiaI,  Climb potential,
I
| ftlmin  |     |     |     |     |     |     | mlsec |     |
| ------- | --- | --- | --- | --- | --- | --- | ----- | --- |
10 -
|     |     |     |     |     | Predicted  |     | 50  |     |
| --- | --- | --- | --- | --- | ---------- | --- | --- | --- |
0
|     | 0   |     |     |     |     |     | 0   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
.8  1.0  1.2  1.4  1.6  1.8  2.0  2.2
M
|     |     | (d)  Altitude = 40.000 ft (12, 192 m).  |     |     |     |     |     |     |
| --- | --- | --------------------------------------- | --- | --- | --- | --- | --- | --- |
Run
|     |     | o A   |     |     |     |     | - 100  |     |
| --- | --- | ----- | --- | --- | --- | --- | ------ | --- |
O B
0  Constant M climb
0
10-
| Climb potential,  | ftlmin  |     |     |     |     |     | 50 Climb potential,  | mlsec  |
| ----------------- | ------- | --- | --- | --- | --- | --- | -------------------- | ------ |
5  QCP
$-Cpredicted
0
|     | 0   | I   |     |     |     |     | 0   |     |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
(e) Altitude = 50,000 ft (15,240 m)
W  w
|     |     |     | Figure 9.  | Concluded.  |     |     |     |     |
| --- | --- | --- | ---------- | ----------- | --- | --- | --- | --- |

|     |             |      | Climb potential.  | mlsec   |         |           |     |
| --- | ----------- | ---- | ----------------- | ------- | ------- | --------- | --- |
|     | 0  100 200  | 0    | 100  200          | 0' 100  | 200  0  | 100  200  |     |
|     | m           |      |                   |         |         |           | ­   |
|     |             | p m  |                   | m       | m       |           |     |
1
5w03
|     |     | 7I  |
   |     |     |     | 15xlOj |
| --- | --- | --- | --- | --- | --- | --- | ------ |
I
Run
10
h,  m
| h, ft  |     |     | 0  0  |     |     |     | 5   |
| ------ | --- | --- | ----- | --- | --- | --- | --- |
0
|     |      |            |                   |               | 0     | 20  4OAO |     |
| --- | ---- | ---------- | ----------------- | ------------- | ----- | -------- | --- |
|     |      |            | Climb potential,  | ftlmin        |       |          |     |
|     |      |            |                   | Wf,  kgls ec  |       |          |     |
|     | 0  1 | 2 3  4   0 | 1 2 3 4           |   0 1 2       | 3 4   |          |     |
|     |      | m          |                   | m             |       |          |     |
|     |      | r          |                   | r             |       |          |     |
40
t
10
0
f t
h'
u
|     | 0  2 4 | 6 8   0 | 2 4 6 8 |   0 2 4 | 6 8   0 2 | 4 6 8 |     |
| --- | ------ | ------- | ------- | ------- | --------- | ----- | --- |
|     |        |         | Wf,     | lblsec  |           |       |     |
40
30
h,  ft
20
0

|     | 10  |     | -0  |     |     |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |
0

|     | o h  |     | 1
 |     |     |     |     |
| --- | ---- | --- | --- | --- | --- | --- | --- |
.5  .7  .6  .8  .6  .8  .8
M
Standard-day  subsonic climb performance of the test airplane at
Figure 10.
a normal load factor of  1, maximum afterburner power,  gross weight of
18,000 pounds (8165 kilograms),  and with no external stores,
34

I

lo

Climb potential,  mlsec
|         | 200 	 |              |         | 200
 |
| ------- | ----- | ------------ | ------- | ----- |
| 0  100  |       | 0  loo  200  | 0  100  |       |
|         |       | m            | m       |       |
1
|     |     | r   |     | 18x1O5  |
| --- | --- | --- | --- | ------- |
14
h,  m
00

| 30t  |     | t   |     | 10  |
| ---- | --- | --- | --- | --- |
u
| 2  o  | l  a  |     | I1  |     |
| ----- | ----- | --- | --- | --- |
6
| 0  20  | 40x103  | 0  20  40x103
 | 0  20  | 40x103
 |
| ------ | ------- | --------------- | ------ | -------- |
F
L
18x1O3

14

| h,  ft 	40  |     |     |     | h,  m  |
| ----------- | --- | --- | --- | ------ |
| 30          |     |     |     | 10     |
0
| 20        |     | 1.7 1.9  |            | 6
  |
| --------- | --- | -------- | ---------- | --- |
| 1.4  1.6  |     |          | 1.8  2.0
 |     |
M
Figure 11.  Standard-day  supersonic climb performance of the test airplane
at a normal load factor of  1, maximum afterburner power,  gross weight of
18,000 pounds (8165 kilograms), and with no external stores.
35
I

|     |      |      |     | VT,  mlsec  |      |     |      |       |
| --- | ---- | ---- | --- | ----------- | ---- | --- | ---- | ----- |
|     | 100  | 200  |     |             |      |     |      |       |
|     |      |      |     | 300         | 400  |     | 500  | 600   |
|     | I    |      |     | I           | I    |     | I    | ~  1  |
~~~
|     |     |     |     |     |     | Climb potential,  | 1000 ft/min (m/sec) |     |
| --- | --- | --- | --- | --- | --- | ----------------- | ------------------- | --- |
0
|     | 501    |     |     |     |     |     | A   |         |
| --- | ------ | --- | --- | --- | --- | --- | --- | ------- |
|     | 60AO3  |     |     |     |     |     |     | (15.2)  |
15
40
~
10  h,  m
5
-1
j
I
I
i
I
n
01
| I(-0  |     |     |     | I   | I   | I   | I   | 1   |
| ----- | --- | --- | --- | --- | --- | --- | --- | --- |
-3
| I-  | 200  400  | 600  | 800  | 1000  | 1200  | 1400  | 1600  | 1800  2000  |
| --- | --------- | ---- | ---- | ----- | ----- | ----- | ----- | ----------- |
I
- I
VT,  ftlsec
N
z

Figure 12.  F-104,  S/N 790, standard-day  climb-potential contours derived from flight at a normal load

- 0I,
factor of 1. niaximum afterburner power, and a gross weight of 18,000 pounds (8165 kilograms).
- cG.3I

NATIONAALE RONAUTICANSD  SPACE ADMINISTRIAOTN
WASHINGTODN., C. 20546
| OFFICIAL BUSINESS  |     |     |     |     |     | FIRST CLASS MAIL  |     |     |
| ------------------ | --- | --- | --- | --- | --- | ----------------- | --- | --- |
PENALTY FOR PRIVATE USE 5900
POSTAGE AND FEES PAID
NATIONAL AERONAUTICS Ab
SPACE ADMINISTRATION
|     |     | 04U 001 27             |              | 51 305  |              |     | 71147  | 00903    |
| --- | --- | ---------------------- | ------------ | ------- | ------------ | --- | ------ | -------- |
|     |     | A I R   FORCE WEAPGNS  |              |         | LABORATORY   |     |        | /WLOL/   |
|     |     | KIRTLAND AFR,          |              |         | NEW  MEXICO  |     | 87117  |          |
|     |     | ATT E.                 | LOU BOWMAN,  |         | CHIEF,TECH.  |     |        | LIBRARY  |
POSTMASTER: 	 If Undeliverable (Section 158
Postal Manual) Do Not Retur
|     |     |     | -   |     | -_-.-- |     |     |     |
| --- | --- | --- | --- | --- | ------ | --- | --- | --- |
| __  |     |  .. |     |     |        | ­   |     |     |
‘The aeronautical and soace activities of the United States shall be
|     | conducted so as to contribzcte . . .  |     |     |     |     |     |     | himian knowl­ |
| --- | ------------------------------------- | --- | --- | --- | --- | --- | --- | ------------- |
to the expansion of
phenomena in the atitiosphere and space. The Administration
edge of
shall provide for the widest practicable and appropriate disseniination
of  inforttiation concerning its actii4ies and the resdts thereof.”
|       |             |     |     | -NATIONAL                   | AERONAUTICASND &‘ACE  |     |     | ACT OF 1958  |
| ----- | ----------- | --- | --- | --------------------------- | --------------------- | --- | --- | ------------ |
| NASA  | SCIENTIFIC  |     |     | AND TECHNICAL PUBLICATIONS  |                       |     |     |              |
TECHNICAL REPORTS: Scientific and  TECHNICAL TRANSLATIONS: Information
technical information considered important,  published in a foreign language considered
complete, and a lasting contribution to existing  to merit NASA distribution in English.
knowledge.
SPECIAL PUBLICATIONS: Information
TECHNICAL NOTES: Information less broad  derived from or of value to NASA activities.
in scope but nevertheless of impprtance as a  Publications include conference proceedings,
contribution to existing knowledge.  monographs, data compilations, handbooks,
sourcebooks, and special bibliographies.
TECHNICAL MEMORANDUMS:
Information receiving limited distribution  TECHNOLOGY UTILIZATION
because of preliminary data, security classifica­ PUBLICATIONS: Information on technology
tion, or other reasons.  used by NASA that may be of particular
interest in commercial and other non-aerospace
CONTRACTOR’REPORTS: Scientific and  applications. Publications include Tech Briefs,
technical information -generated under a NASA
|     |     |     |     |     |     | Technology Utilization  |     | Reports and  |
| --- | --- | --- | --- | --- | --- | ----------------------- | --- | ------------ |
contract Or grant and considered an important
Technology Surveys.
contribution to existing kn,owledge.
|           | Details on the availability of  |                        |     |     | lhese publications may be obtained from:  |                     |     |                 |
| --------- | ------------------------------- | ---------------------- | --- | --- | ----------------------------------------- | ------------------- | --- | --------------- |
|           | SCIENTIFIC AND TECHNICAL        |                        |     |     |                                           | INFORMATION OFFICE  |     |                 |
| NATIONAL  |                                 | AERONAUTICS AND SPACE  |     |     |                                           |                     |     | ADMINISTRATION  |
Washington, D.C. 90546