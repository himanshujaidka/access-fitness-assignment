import hudson.security.FullControlOnceLoggedInAuthorizationStrategy
import hudson.security.HudsonPrivateSecurityRealm
import hudson.plugins.git.BranchSpec
import hudson.plugins.git.GitSCM
import hudson.plugins.git.UserRemoteConfig
import jenkins.model.Jenkins
import jenkins.model.JenkinsLocationConfiguration
import org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition
import org.jenkinsci.plugins.workflow.job.WorkflowJob
import org.jenkinsci.plugins.workflow.job.properties.PipelineTriggersJobProperty
import hudson.triggers.SCMTrigger

def jenkins = Jenkins.get()
if (!(jenkins.securityRealm instanceof HudsonPrivateSecurityRealm)) {
    def realm = new HudsonPrivateSecurityRealm(false)
    def password = new File('/run/secrets/jenkins_admin_password').text.trim()
    if (password.length() < 24) {
        throw new IllegalStateException('A strong Jenkins admin password is required')
    }
    realm.createAccount('admin', password)
    jenkins.setSecurityRealm(realm)
}

def authorization = new FullControlOnceLoggedInAuthorizationStrategy()
authorization.setAllowAnonymousRead(false)
jenkins.setAuthorizationStrategy(authorization)
jenkins.setNumExecutors(1)
JenkinsLocationConfiguration.get().setUrl('http://localhost:8081/')

if (jenkins.getItem('aceest-fitness') == null) {
    def job = jenkins.createProject(WorkflowJob, 'aceest-fitness')
    def scm = new GitSCM(
        [new UserRemoteConfig(
            'https://github.com/himanshujaidka/access-fitness-assignment.git',
            null, null, null
        )],
        [new BranchSpec('*/main')],
        false, [], null, null, []
    )
    def definition = new CpsScmFlowDefinition(scm, 'Jenkinsfile')
    definition.setLightweight(true)
    job.setDefinition(definition)
    job.addProperty(new PipelineTriggersJobProperty([new SCMTrigger('H/5 * * * *')]))
    job.save()
}
jenkins.save()
