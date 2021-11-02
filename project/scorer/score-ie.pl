#!/usr/bin/perl

# USAGE: perl score-ie.pl <output_templates> <gold_templates>

# This program produces two forms of output:
#
# 1) It prints (to standard output) a table showing the recall, precision, and 
#    F scores for the output templates by comparing them with the gold 
#    templates. 
#
# 2) It prints a file named <output_templates>.trace in the working directory that 
#    displays the recall, precision, and F scores for each individual story. 
#    The overall scores across ALL stories is also appended at the end. 
#    

# **********************************************************************
#                         DATA STRUCTURES
# **********************************************************************

use Class::Struct; 

struct template => {
  id => '$',
  acquired => '$',
  acqbus => '$',
  acqlocs => '$',
  dlramts => '$',
  purchasers => '$',
  sellers => '$',
  status => '$',
  bogus => '$',
}; 

# **********************************************************************
#                         GLOBAL VARIABLES
# **********************************************************************

$response_file = $ARGV[0];
$answerkey_file = $ARGV[1];

# create trace file with same name as response file + extension .trace
$trace_file = $response_file . ".trace";
open(trace_stream, ">$trace_file") || 
    die "Can't open file: $trace_file\n"; 

my($responses, $answerkeys);  # each is a list of template structures
my($alltemplates_correct) = 0;
my($alltemplates_generated) = 0;
my($alltemplates_true) = 0;
my($alltemplates_acquireds_correct) = 0;
my($alltemplates_acquireds_generated) = 0;
my($alltemplates_acquireds_true) = 0;
my($alltemplates_acqbus_correct) = 0;
my($alltemplates_acqbus_generated) = 0;
my($alltemplates_acqbus_true) = 0;
my($alltemplates_acqlocs_correct) = 0;
my($alltemplates_acqlocs_generated) = 0;
my($alltemplates_acqlocs_true) = 0;
my($alltemplates_dlramts_correct) = 0;
my($alltemplates_dlramts_generated) = 0;
my($alltemplates_dlramts_true) = 0;
my($alltemplates_purchasers_correct) = 0;
my($alltemplates_purchasers_generated) = 0;
my($alltemplates_purchasers_true) = 0;
my($alltemplates_sellers_correct) = 0;
my($alltemplates_sellers_generated) = 0;
my($alltemplates_sellers_true) = 0;
my($alltemplates_status_correct) = 0;
my($alltemplates_status_generated) = 0;
my($alltemplates_status_true) = 0;


# **********************************************************************
#                         MAIN CODE
# **********************************************************************

$responses = read_templates($response_file);
$answerkeys = read_templates($answerkey_file);
my($num_anskeys) = scalar @$answerkeys;
score_responses($responses, $answerkeys);

# Print score report for stats over ALL templates
#
print trace_stream "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>";
print trace_stream ">>>>>>>>>>>>>>>>>>>>>>>\n\n";
print_score_report("ALL Templates", $alltemplates_acquireds_correct,
   $alltemplates_acquireds_generated, $alltemplates_acquireds_true, 
   $alltemplates_acqbus_correct, $alltemplates_acqbus_generated,  
   $alltemplates_acqbus_true, $alltemplates_acqlocs_correct, 
   $alltemplates_acqlocs_generated, $alltemplates_acqlocs_true,  
   $alltemplates_dlramts_correct, $alltemplates_dlramts_generated, 
   $alltemplates_dlramts_true, $alltemplates_purchasers_correct, 
   $alltemplates_purchasers_generated, $alltemplates_purchasers_true, 
   $alltemplates_sellers_correct, $alltemplates_sellers_generated, 
   $alltemplates_sellers_true, $alltemplates_status_correct, $alltemplates_status_generated, 
   $alltemplates_status_true, $alltemplates_correct, 
   $alltemplates_generated, $alltemplates_true);

# Display summary score report to standard output
#
display_score_report("ALL Templates", $alltemplates_acquireds_correct,
   $alltemplates_acquireds_generated, $alltemplates_acquireds_true,
   $alltemplates_acqbus_correct, $alltemplates_acqbus_generated,  
   $alltemplates_acqbus_true, $alltemplates_acqlocs_correct, 
   $alltemplates_acqlocs_generated, $alltemplates_acqlocs_true,  
   $alltemplates_dlramts_correct, $alltemplates_dlramts_generated, 
   $alltemplates_dlramts_true, $alltemplates_purchasers_correct, 
   $alltemplates_purchasers_generated, $alltemplates_purchasers_true, 
   $alltemplates_sellers_correct, $alltemplates_sellers_generated, 
   $alltemplates_sellers_true, $alltemplates_status_correct, $alltemplates_status_generated, 
   $alltemplates_status_true, $alltemplates_correct, 
   $alltemplates_generated, $alltemplates_true);


# **********************************************************************
#                         SCORING FUNCTIONS
# **********************************************************************

sub score_responses {
    my($responses, $answerkeys) = @_;
    my($i);
    
    $num_responses = @$responses;
    $num_answerkeys = @$answerkeys;
    if (!($num_responses eq $num_answerkeys)) {
	print "**********************************************************\n";
	print "            WARNING!!!! unequal template sets\n";
	print "            $num_responses responses, $num_answerkeys answerkeys\n";
	print "**********************************************************\n";
	for ($i=0; $i < $num_responses; $i++) {
	    $rtemplate = @$responses[$i];
	    $ktemplate = @$answerkeys[$i];
	    my($rid) = "none"; my($kid) = "none";
	    $rid = $rtemplate->id;
	    if ($ktemplate) {
		$kid = $ktemplate->id;
	    }
	    if ($rid !~ /\s*$kid\s*/i) {
		print "MISMATCH: response=$rid  answerkey=$kid\n";
	    }
	}
    }
    else {
	for ($i=0; $i < $num_responses; $i++) {
	    $response = @$responses[$i];
	    $answerkey = @$answerkeys[$i];
	    $response_id = $response->id;
	    $answerkey_id = $answerkey->id;
	    if ($response_id !~ /^$answerkey_id$/i) { # gut check
		print "WARNING: mismatched templates";
		print " ($response_id and $answerkey_id)\n";
	    }
	    else {
		print "Processing text $response_id ...\n";
		print trace_stream "\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>";
		print trace_stream ">>>>>>>>>>>>>>>>>>>>>>>\n\n";
		print trace_stream "     GOLD ANSWER KEY \n\n";
		print_template($answerkey);
		print trace_stream "\n     SYSTEM OUTPUT \n\n";
		print_template($response);
		score_template($response, $answerkey);
	    }
	}
    }
}

sub score_template {
    my($response, $key) = @_;
    my($correct_acquired, $generated_acquired, $true_acquired) = 0;
    my($correct_acqbus, $generated_acqbus, $true_acqbus) = 0;
    my($correct_acqlocs, $generated_acqlocs, $true_acqlocs) = 0;
    my($correct_dlramts, $generated_dlramts, $true_dlramts) = 0;
    my($correct_purchasers, $generated_purchasers, $true_purchasers) = 0;
    my($correct_sellers, $generated_sellers, $true_sellers) = 0;
    my($correct_status, $generated_status, $true_status) = 0;
    my($total_correct, $total_generated, $total_true) = 0;

#     my(@key_acquireds) = ();
#     push(@key_acquireds, $key->acquired);
#     if (member($response->acquired, \@key_acquireds)) {  # member function handles
# 	$correct_acquired++;                             # disjunctions
# 	$generated_acquired++;
# 	$total_correct++;
# 	$total_generated++;
#     }
#     else {
# 	$correct_acquired = 0;
# 	if ($response->acquired !~ /^---$/) {  # make sure slot filled
# 	    $generated_acquired++;
# 	    $total_generated++;
# 	}
# 	else {
# 	    $generated_acquired = 0;
# 	}
#     }
#     $total_true = 1;   # for acquired slot

    $response_acquired = $response->acquired;
    $key_acquired = $key->acquired;
    $generated_acquired = @$response_acquired;
    $true_acquired = @$key_acquired;
    foreach $acquired (@$response_acquired) {
	if ($found = member($acquired, $key_acquired)) {
	    $correct_acquired++;
	    $key_acquired = remove($found, $key_acquired);
	}
    }

    $response_acqbus = $response->acqbus;
    $key_acqbus = $key->acqbus;
    $generated_acqbus = @$response_acqbus;
    $true_acqbus = @$key_acqbus;
    foreach $bus (@$response_acqbus) {
	if ($found = member($bus, $key_acqbus)) {
	    $correct_acqbus++;
	    $key_acqbus = remove($found, $key_acqbus);
	}
    }

    $response_acqlocs = $response->acqlocs;
    $key_acqlocs = $key->acqlocs;
    $generated_acqlocs = @$response_acqlocs;
    $true_acqlocs = @$key_acqlocs;
    foreach $bus (@$response_acqlocs) {
	if ($found = member($bus, $key_acqlocs)) {
	    $correct_acqlocs++;
	    $key_acqlocs = remove($found, $key_acqlocs);
	}
    }

    $response_dlramts = $response->dlramts;
    $key_dlramts = $key->dlramts;
    $generated_dlramts = @$response_dlramts;
    $true_dlramts = @$key_dlramts;
    foreach $bus (@$response_dlramts) {
	if ($found = member($bus, $key_dlramts)) {
	    $correct_dlramts++;
	    $key_dlramts = remove($found, $key_dlramts);
	}
    }

    $response_purchasers = $response->purchasers;
    $key_purchasers = $key->purchasers;
    $generated_purchasers = @$response_purchasers;
    $true_purchasers = @$key_purchasers;
    foreach $bus (@$response_purchasers) {
	if ($found = member($bus, $key_purchasers)) {
	    $correct_purchasers++;
	    $key_purchasers = remove($found, $key_purchasers);
	}
    }

    $response_sellers = $response->sellers;
    $key_sellers = $key->sellers;
    $generated_sellers = @$response_sellers;
    $true_sellers = @$key_sellers;
    foreach $bus (@$response_sellers) {
	if ($found = member($bus, $key_sellers)) {
	    $correct_sellers++;
	    $key_sellers = remove($found, $key_sellers);
	}
    }

    $response_status = $response->status;
    $key_status = $key->status;
    $generated_status = @$response_status;
    $true_status = @$key_status;
    foreach $bus (@$response_status) {
	if ($found = member($bus, $key_status)) {
	    $correct_status++;
	    $key_status = remove($found, $key_status);
	}
    }

    $total_correct = $total_correct + $correct_acquired + $correct_acqbus + 
	$correct_acqlocs + $correct_dlramts + $correct_purchasers + 
        $correct_sellers + $correct_status;  
    $total_generated = $total_generated + $generated_acquired + $generated_acqbus + 
	$generated_acqlocs + $generated_dlramts + 
	$generated_purchasers + $generated_sellers + $generated_status;
    $total_true = $total_true + $true_acquired + $true_acqbus + $true_acqlocs +
	$true_dlramts + $true_purchasers + $true_sellers + $true_status;
    
    print_score_report($response->id, $correct_acquired, 
       $generated_acquired, $true_acquired,
       $correct_acqbus, $generated_acqbus, $true_acqbus,
       $correct_acqlocs, $generated_acqlocs, $true_acqlocs, 
       $correct_dlramts, $generated_dlramts, $true_dlramts, 
       $correct_purchasers, $generated_purchasers, $true_purchasers, 
       $correct_sellers, $generated_sellers, $true_sellers,
       $correct_status, $generated_status, $true_status,
       $total_correct, $total_generated, $total_true);

    update_global_vars($correct_acquired, $generated_acquired, $true_acquired,
       $correct_acqbus, $generated_acqbus, $true_acqbus, 
       $correct_acqlocs, $generated_acqlocs, $true_acqlocs, 
       $correct_dlramts, $generated_dlramts, $true_dlramts, 
       $correct_purchasers, $generated_purchasers, $true_purchasers, 
       $correct_sellers, $generated_sellers, $true_sellers, 
       $correct_status, $generated_status, $true_status, 
       $total_correct, $total_generated, $total_true);
}


# Remove just the *first* occurrence of the item from the list.
# IMPORTANT because some templates (e.g., 0945) contain separate
# entries for the same string (e.g., two distinct occurrences of "PEOPLE").
#
sub remove {
    my($item, $lst) = @_;

    my(@newlst) = ();
    my($found) = 0;
    for ($i=0; $i < @$lst; $i++) {
	if (($found == 0) && (@$lst[$i] eq $item)) {
	    $found = 1;
	}
	else {
	    push(@newlst, @$lst[$i]);
	}
    }
    return(\@newlst);
}


# $answers is a list of possible answers.
# EACH $answer may be a disjunction of options:  option1 / option2 / ...
# If any of the options matches the string, then this is a match
#
sub member {
    my($string, $answers) = @_;

    foreach $answer (@$answers) {
	@options = split /\//, $answer;
	foreach $option (@options) {
	    if (match($option, $string)) {
#		print "Found match: $string $option\n";
		return($answer);  # return ENTIRE answer string
	    }
	}
    }
    return(0);
}

sub match {
    my($str1, $str2) = @_;

    if ($str1 =~ /^\s*\Q$str2\E\s*$/i) {  # allows white space on ends
	return(1);
    }
    else {
	return(0);
    }
}



sub print_score_report {
    my($id, $correct_acquired, $generated_acquired, $true_acquired,
       $correct_acqbus, $generated_acqbus, $true_acqbus, $correct_acqlocs, 
       $generated_acqlocs, $true_acqlocs, $correct_dlramts, 
       $generated_dlramts, $true_dlramts, $correct_purchasers, 
       $generated_purchasers, $true_purchasers, $correct_sellers, 
       $generated_sellers, $true_sellers, $correct_status, 
       $generated_status, $true_status, $total_correct, 
       $total_generated, $total_true) = @_;

#    print trace_stream "\n********************************************************\n";
    print trace_stream "\n     SCORES for $id\n\n";
#    print trace_stream "********************************************************\n";
    print trace_stream "                RECALL             PRECISION          F-SCORE\n";
    print_scores("ACQUIRED", $correct_acquired, $generated_acquired, $true_acquired);
    print_scores("ACQBUS", $correct_acqbus, $generated_acqbus, $true_acqbus);
    print_scores("ACQLOC", $correct_acqlocs, $generated_acqlocs, $true_acqlocs);
    print_scores("DLRAMT", $correct_dlramts, $generated_dlramts, $true_dlramts);
    print_scores("PURCHASER", $correct_purchasers, $generated_purchasers, $true_purchasers);
    print_scores("SELLER", $correct_sellers, $generated_sellers, $true_sellers);
    print_scores("STATUS", $correct_status, $generated_status, $true_status);

#    print trace_stream "--------------------------------------------------------\n";
#    print trace_stream "---------------------------------------------------------------\n";
    print trace_stream "--------        --------------     --------------     ----\n";
    print_scores("TOTAL", $total_correct, $total_generated, $total_true);
}


sub display_score_report {
    my($id, $correct_acquired, $generated_acquired, $true_acquired,
       $correct_acqbus, $generated_acqbus, $true_acqbus, $correct_acqlocs, 
       $generated_acqlocs, $true_acqlocs, $correct_dlramts, 
       $generated_dlramts, $true_dlramts, $correct_purchasers, 
       $generated_purchasers, $true_purchasers, $correct_sellers, 
       $generated_sellers, $true_sellers, $correct_status, 
       $generated_status, $true_status, $total_correct, 
       $total_generated, $total_true) = @_;

#    print "\n********************************************************\n";
    print "\n     Scores for $id\n\n";
#    print "********************************************************\n";
    print "                RECALL             PRECISION          F-SCORE\n";
    display_scores("ACQUIRED", $correct_acquired, $generated_acquired, 
		 $true_acquired);
    display_scores("ACQBUS", $correct_acqbus, $generated_acqbus, 
		 $true_acqbus);
    display_scores("ACQLOC", $correct_acqlocs,
		 $generated_acqlocs, $true_acqlocs);
    display_scores("DLRAMT", $correct_dlramts, $generated_dlramts, 
		 $true_dlramts);
    display_scores("PURCHASER", $correct_purchasers, $generated_purchasers, 
		 $true_purchasers);
    display_scores("SELLER", $correct_sellers, $generated_sellers, $true_sellers);
    display_scores("STATUS", $correct_status, $generated_status, $true_status);
#    print "--------------------------------------------------------\n";
#    print "---------------------------------------------------------------\n";
    print "--------        --------------     --------------     ----\n";
    display_scores("TOTAL", $total_correct, $total_generated, $total_true);
}



# Update global variables
sub update_global_vars {
    my($correct_acquired, $generated_acquired, $true_acquired,
       $correct_acqbus, 
       $generated_acqbus, $true_acqbus, $correct_acqlocs, 
       $generated_acqlocs, $true_acqlocs, $correct_dlramts, 
       $generated_dlramts, $true_dlramts, $correct_purchasers, 
       $generated_purchasers, $true_purchasers, $correct_sellers, 
       $generated_sellers, $true_sellers, $correct_status, 
       $generated_status, $true_status, $total_correct, 
       $total_generated, $total_true) = @_;

    $alltemplates_correct += $total_correct;
    $alltemplates_generated += $total_generated;
    $alltemplates_true += $total_true;
    $alltemplates_acquireds_correct += $correct_acquired;
    $alltemplates_acquireds_generated += $generated_acquired;
    $alltemplates_acquireds_true += $true_acquired;
    $alltemplates_acqbus_correct += $correct_acqbus; 
    $alltemplates_acqbus_generated += $generated_acqbus; 
    $alltemplates_acqbus_true += $true_acqbus; 
    $alltemplates_acqlocs_correct += $correct_acqlocs; 
    $alltemplates_acqlocs_generated += $generated_acqlocs; 
    $alltemplates_acqlocs_true += $true_acqlocs; 
    $alltemplates_dlramts_correct += $correct_dlramts; 
    $alltemplates_dlramts_generated += $generated_dlramts; 
    $alltemplates_dlramts_true += $true_dlramts; 
    $alltemplates_purchasers_correct += $correct_purchasers; 
    $alltemplates_purchasers_generated += $generated_purchasers; 
    $alltemplates_purchasers_true += $true_purchasers; 
    $alltemplates_sellers_correct += $correct_sellers; 
    $alltemplates_sellers_generated += $generated_sellers; 
    $alltemplates_sellers_true += $true_sellers; 
    $alltemplates_status_correct += $correct_status; 
    $alltemplates_status_generated += $generated_status; 
    $alltemplates_status_true += $true_status; 
} 


sub print_scores {
    my($label, $correct, $guessed, $true) = @_;
    my($tally, $padded_tally);

    if ($true == 0) {
	$recall = 0;
    }
    else {
	$recall = $correct / $true;
    }
    if ($guessed == 0) {
	$precision = 0;
    }
    else {
	$precision = $correct / $guessed;
    }
    if (($precision + $recall) == 0) {
	$fmeasure = 0;
    }
    else {
	$fmeasure = (2 * $precision * $recall) / ($precision + $recall);
    }

    $padded_label = pad_w_spaces($label, 15);
    print trace_stream "$padded_label ";
    printf trace_stream "%.2f", $recall;
    print trace_stream " ($correct/$true)\t   ";
    printf trace_stream "%.2f", $precision;
    $tally = sprintf "(%d/%d)", $correct, $guessed;
    $padded_tally = pad_w_spaces($tally, 14);
    print trace_stream " $padded_tally";
    printf trace_stream "%.2f\n", $fmeasure;

}

sub display_scores {
    my($label, $correct, $guessed, $true) = @_;
    my($recall, $precision, $fmeasure, $tally, $padded_tally);

    if ($true eq 0) {
	$recall = 0;
    }
    else {
	$recall = $correct / $true;
    }
    if ($guessed eq 0) {
	$precision = 0;
    }
    else {
	$precision = $correct / $guessed;
    }
    if (($precision + $recall) == 0) {
	$fmeasure = 0;
    }
    else {
	$fmeasure = (2 * $precision * $recall) / ($precision + $recall);
    }
    
    $padded_label = pad_w_spaces($label, 15);
    print "$padded_label ";
    printf "%.2f", $recall;
    print  " ($correct/$true)\t   ";
    printf "%.2f", $precision;
    $tally = sprintf "(%d/%d)", $correct, $guessed;
    $padded_tally = pad_w_spaces($tally, 14);
    print " $padded_tally";
    printf "%.2f\n", $fmeasure;
}

# **********************************************************************
#                         I/O
# **********************************************************************

sub read_templates {
    my($filename) = @_;
    my($line, $id, $acquired, $bus, $acqloc, $dlramt);
    my($purchaser, $seller, $status, $last_slot, $template);
    my(@templates) = ();

    my($id) = "";
    $last_slot = "";
    my(@acquireds, @acqbus, @acqlocs, @dlramts, @purchasers, @sellers, @statuses) = ();
    open(stream, $filename) || die "Can't open file: $filename\n";
    while ($line = <stream>) {
	$line =~ s/\n//g;  # strip newline
	if ($line =~ /^\s*$/) {  # if blank line, do nothing
	}
	elsif ($line =~ /^TEXT:\s+(.*)$/i) {
	    if ($id) {  # save previous template, starting new one
		$template = create_template($id, \@acquireds, \@acqbus,
		      \@acqlocs, \@dlramts, \@purchasers, \@sellers, \@statuses);
		push(@templates, $template);
	    }
            @acquireds = (); @acqbus = (); @acqlocs = (); @dlramts = (); @purchasers = (); @sellers = (); @statuses = (); # reinitialize
	    $id = $1;
	    $id =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "id";
	}
	elsif ($line =~ /^ACQUIRED:\s+(.*)$/i) {
	    $acquired = $1;
	    $acquired =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "acquired";
	    if ($acquired !~ /^---$/i) {
		push(@acquireds, $acquired);
	    }
	}
	elsif ($line =~ /^ACQBUS:\s+(.*)$/i) {
	    $bus = $1;
	    $bus =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "bus";
	    if ($bus !~ /^---$/i) {
		push(@acqbus, $bus);
	    }
	}
	elsif ($line =~ /^ACQLOC:\s+(.*)$/i) {
	    $acqloc = $1;
	    $acqloc =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "acqloc";
	    if ($acqloc !~ /^---$/i) {
		push(@acqlocs, $acqloc);
	    }
	}
	elsif ($line =~ /^DLRAMT:\s+(.*)$/i) {
	    $dlramt = $1;
	    $dlramt =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "dlramt";
	    if ($dlramt !~ /^---$/i) {
		push(@dlramts, $dlramt);
	    }
	}
	elsif ($line =~ /^PURCHASER:\s+(.*)$/i) {
	    $purchaser = $1;
	    $purchaser =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "purchaser";
	    if ($purchaser !~ /^---$/i) {
		push(@purchasers, $purchaser);
	    }
	}
	elsif ($line =~ /^SELLER:\s+(.*)$/i) {
	    $seller = $1;
	    $seller =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "seller";
	    if ($seller !~ /^---$/i) {
		push(@sellers, $seller);
	    }
	}
	elsif ($line =~ /^STATUS:\s+(.*)$/i) {
	    $status = $1;
	    $status =~ s/\s+$//;  # remove trailing white space
	    $last_slot = "seller";
	    if ($status !~ /^---$/i) {
		push(@statuses, $status);
	    }
	}
	elsif ($line =~ /^\s+([\w\d].*)/i) {
	    $item = $1;
	    $item =~ s/\s+$//;  # remove trailing white space
	    if ($last_slot =~ /bus/i) {
		push(@acqbus, $item);
	    }
	    elsif ($last_slot =~ /acqloc/i) {
		push(@acqlocs, $item);
	    }
	    elsif ($last_slot =~ /dlramt/i) {
		push(@dlramts, $item);
	    }
	    elsif ($last_slot =~ /purchaser/i) {
		push(@purchasers, $item);
	    }
	    elsif ($last_slot =~ /seller/i) {
		push(@sellers, $item);
	    }
	    elsif ($last_slot =~ /status/i) {
		push(@statuses, $item);
	    }
	}
    }
#    for ($i=0; $i < @acqbus; $i++) {
#	print("Creating ACQBUS = ", @acqbus[$i], "\n");
#    }
    # don't forget last one!
    $template = create_template($id, \@acquireds, \@acqbus,
		\@acqlocs, \@dlramts, \@purchasers, \@sellers, \@statuses);
    push(@templates, $template);
    return(\@templates);
}

sub create_template {
    my($id, $acquireds, $acqbus, $acqlocs, $dlramts, $purchasers, $sellers, $statuses) = @_;
    my($template);

    my(@newacquireds) = @$acquireds;
    my(@newacqbus) = @$acqbus;
    my(@newacqlocs) = @$acqlocs;
    my(@newdlramts) = @$dlramts;
    my(@newpurchasers) = @$purchasers;    
    my(@newsellers) = @$sellers;  # copy list
    my(@newstatuses) = @$statuses;  # copy list

    $template = template->new();
    $template->id($id);
    $template->acquired(\@newacquireds);
    $template->acqbus(\@newacqbus);
    $template->acqlocs(\@newacqlocs);
    $template->dlramts(\@newdlramts);
    $template->purchasers(\@newpurchasers);
    $template->sellers(\@newsellers);
    $template->status(\@newstatuses);
    return($template);
}

sub print_template {
    my($template) = @_;
    my($label, $id, $acquireds, $acqbus, $acqlocs, $dlramts);
    my($purchasers, $sellers, $status);

    $label = pad_w_spaces("TEXT:", 15);
    $id = $template->id;
    print trace_stream "$label $id\n";

#     $label = pad_w_spaces("ACQUIRED:", 15);
#     $acquired = $template->acquired;
#     print trace_stream "$label $acquired\n";

    $acquireds = $template->acquired;	
    $label = pad_w_spaces("ACQUIRED:", 15);
    if (@$acquireds eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$acquireds; $i++) {
	    $acquired = @$acquireds[$i];
	    print trace_stream "$label $acquired\n";
	    $label = pad_w_spaces("", 15);
	}
    }
    $acqbuses = $template->acqbus;	
    $label = pad_w_spaces("ACQBUS:", 15);
    if (@$acqbuses eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$acqbuses; $i++) {
	    $bus = @$acqbuses[$i];
	    print trace_stream "$label $bus\n";
	    $label = pad_w_spaces("", 15);
	}
    }

    $acqlocs = $template->acqlocs;	
    $label = pad_w_spaces("ACQLOC:", 15);
    if (@$acqlocs eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$acqlocs; $i++) {
	    $acqloc = @$acqlocs[$i];
	    print trace_stream "$label $acqloc\n";
	    $label = pad_w_spaces("", 15);
	}
    }

    $dlramts = $template->dlramts;	
    $label = pad_w_spaces("DLRAMT:", 15);
    if (@$dlramts eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$dlramts; $i++) {
	    $dlramt = @$dlramts[$i];
	    print trace_stream "$label $dlramt\n";
	    $label = pad_w_spaces("", 15);
	}
    }

    $purchasers = $template->purchasers;	
    $label = pad_w_spaces("PURCHASER:", 15);
    if (@$purchasers eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$purchasers; $i++) {
	    $purchaser = @$purchasers[$i];
	    print trace_stream "$label $purchaser\n";
	    $label = pad_w_spaces("", 15);
	}
    }

    $sellers = $template->sellers;	
    $label = pad_w_spaces("SELLER:", 15);
    if (@$sellers eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$sellers; $i++) {
	    $seller = @$sellers[$i];
	    print trace_stream "$label $seller\n";
	    $label = pad_w_spaces("", 15);
	}
    }

    $statuses = $template->status;	
    $label = pad_w_spaces("STATUS:", 15);
    if (@$statuses eq 0) {
	print trace_stream "$label ---\n";
    }
    else {
	for ($i=0; $i < @$statuses; $i++) {
	    $status = @$statuses[$i];
	    print trace_stream "$label $status\n";
	    $label = pad_w_spaces("", 15);
	}
    }
}



# Given a string and number N, this function pads spaces onto the right
# side of the string until the string has length N.
#
sub pad_w_spaces {
    my($str,$N) = @_;

    my($len) = length $str;
    while ($len < $N) {
        $str = $str . " ";
        $len = length $str;
    }
    return($str);
}


