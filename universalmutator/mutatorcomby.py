from __future__ import print_function

import re
import pkg_resources
import random

from comby import Comby


def compileRules(ruleFiles):
    rulesText = []

    for ruleFile in ruleFiles:
        if ".rules" not in ruleFile:
            ruleFile += ".rules"
        try:
            with pkg_resources.resource_stream('universalmutator', 'comby/' + ruleFile) as builtInRule:
                for line in builtInRule:
                    line = line.decode()
                    rulesText.append((line, "builtin:" + ruleFile))
        except BaseException:
            print("FAILED TO FIND RULE", ruleFile, "AS BUILT-IN...")
            try:
                with open(ruleFile, 'r') as file:
                    for l in file:
                        rulesText.append((l, ruleFile))
            except BaseException:
                print("COULD NOT FIND RULE FILE", ruleFile + "!  SKIPPING...")

    rules = []
    ignoreRules = []
    skipRules = []
    ruleLineNo = 0

    for (r, ruleSource) in rulesText:
        ruleLineNo += 1
        if r == "\n":
            continue
        if " ==> " not in r:
            if " ==>" in r:
                s = r.split(" ==>")
            else:
                if r[0] == "#":  # Don't warn about comments
                    continue
                print("*" * 60)
                print("WARNING:")
                print("RULE:", r, "FROM", ruleSource)
                print("DOES NOT MATCH EXPECTED FORMAT, AND SO WAS IGNORED")
                print("*" * 60)
                continue  # Allow blank lines and comments, just ignore lines without a transformation
        else:
            s = r.split(" ==> ")
            lhs = s[0]

        lhs = lhs.rstrip() # RVT(XXX) trailing whitespace in match will be treated significantly, so strip it. But stripping it means we can't specify it.
        if (len(s[1]) > 0) and (s[1][-1] == "\n"):
            rhs = s[1][:-1]
        else:
            rhs = s[1]
        if rhs == "DO_NOT_MUTATE":
            ignoreRules.append(lhs)
        elif rhs == "SKIP_MUTATING_REST":
            skipRules.append(lhs)
        else:
            rules.append(((lhs, rhs), (r, ruleSource + ":" + str(ruleLineNo))))


    return (rules, ignoreRules, skipRules)


def mutants(source, ruleFiles=["universal.rules"], mutateTestCode=False, mutateBoth=False,
            ignorePatterns=None, ignoreStringOnly=False, fuzzing=False):

    comby = Comby()

    print("MUTATING WITH RULES:", ", ".join(ruleFiles))

    (rules, ignoreRules, skipRules) = compileRules(ruleFiles)

    for p in ignorePatterns:
        ignoreRules.append(lhs)

    source = ''.join(source)

    mutants = []
    # Instead of line-by-line x rule-by-rule iterate rule-by-rule x match-by-match.
    for ((lhs, rhs), ruleUsed) in rules:
        for match in comby.matches(source, lhs): # FIXME(RVT): add language
            environment = dict()
            for entry in match.environment:
                environment[entry] = match.environment.get(entry).fragment
            mutant = comby.substitute(rhs, environment)
            substitutionRange = (match.location.start.offset, match.location.stop.offset)
            mutants.append((substitutionRange, mutant, ruleUsed))

    return mutants


# Mutant is a tuple (<range to of matching source (in file offsets) that will be replaced by mutant fragment>, <mutant fragment>, <rule used>)
# Example: ((41, 58), 'improved_myfunction(x)', 'foo ==> bar')
# Ranges may not be unicode friendly...
def makeMutant(source, mutant, path):
    sourceBeforeFragment = source[:mutant[0][0]]
    sourceAfterFragment = source[mutant[0][1]:]
    mutantSource = sourceBeforeFragment + mutant[1] + sourceAfterFragment
    with open(path, 'w') as file:
        file.write(mutantSource)
